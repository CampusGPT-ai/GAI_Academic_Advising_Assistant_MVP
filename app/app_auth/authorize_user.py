from fastapi import HTTPException, Depends
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt, json
from jwt import PyJWKClient
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Request
import os
from datetime import datetime, timedelta
from data.models import UserSession, Profile
import logging
from settings.settings import Settings
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from starlette.responses import RedirectResponse

settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

from fastapi.responses import JSONResponse

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

CLIENT_ID = settings.AZURE_CLIENT_ID
TENANT_ID = settings.AZURE_TENANT_ID
CLIENT_SECRET = settings.AZURE_CLIENT_SECRET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)) -> Optional[str]:
    issuer_url = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/v2.0"
    jwks_client = PyJWKClient(f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/discovery/v2.0/keys")
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    try:
        payload = jwt.decode(
        token, 
        signing_key.key, 
        algorithms=["RS256"], 
        audience=CLIENT_ID, 
        issuer=issuer_url,
        options={"verify_signature": True, "verify_aud": True, "verify_iss": True}
        )
        
        logger.info("got token payload %s", payload)
        try:
            user = create_user_if_not_exist(payload)
            return user
        except Exception as e:
            raise e
    
    except:
        raise credentials_exception
    
def create_user_if_not_exist(payload):
    try:
        user_id: str = payload.get("sub")
        first_name: str = payload.get("name")
        last_name: str = payload.get("last_name")
        email: str = payload.get("preferred_username")
        created_at =datetime.utcnow
        updated_at = datetime.utcnow
        considerations = []
        user = Profile.objects(user_id=user_id).first()
        if not user:
            user =  Profile(user_id=user_id, first_name=first_name, last_name=last_name, email=email, created_at=created_at, updated_at=updated_at, considerations=considerations)
            user.save()
    except Exception as e:
        print(f"Error saving user profile to the database: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return user

async def prepare_from_fastapi_request(request, debug=False):
  form_data = await request.form()
  rv = {
    "http_host": request.client.host,
    "server_port": request.url.port,
    "script_name": request.url.path,
    "post_data": { },
    "get_data": { },
  }
  if (request.query_params):
    rv["get_data"] = request.query_params,
  if "SAMLResponse" in form_data:
    SAMLResponse = form_data["SAMLResponse"]
    rv["post_data"]["SAMLResponse"] = SAMLResponse
  if "RelayState" in form_data:
    RelayState = form_data["RelayState"]
    rv["post_data"]["RelayState"] = RelayState
  return rv

idp_settings = OneLogin_Saml2_IdPMetadataParser.parse_remote(settings.SAML_METADATA_URL)
saml_settings = {
  "strict": True,
  "debug": True,
  "sp": {
    "entityId": "test-saml-client",
    "assertionConsumerService": {
      "url": f"{settings.BASE_URL}/validate_token_saml",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    },
    "x509cert": settings.SAML_CERT
  }
}
idp_settings.update(saml_settings)
saml_settings_obj = OneLogin_Saml2_Settings(idp_settings)

@router.get("/saml/login")
async def saml_login(request: Request):
    logger.info(f"SAML Settings: {idp_settings}")
    req = await prepare_from_fastapi_request(request)

    auth = OneLogin_Saml2_Auth(req, saml_settings_obj)
    callback_url = auth.login(return_to=settings.CLIENT_BASE_URL)
    response = RedirectResponse(url=callback_url)
    return response

@router.post("/validate_token_saml")
async def saml_login_callback(request: Request):
    req = await prepare_from_fastapi_request(request)

    auth = OneLogin_Saml2_Auth(req, saml_settings_obj)
    auth.process_response()
    errors = auth.get_errors()
    if len(errors) == 0:

        if not auth.is_authenticated():
            logger.error("No user info retrieved, authentication information may be invalid")
            raise credentials_exception
        else:
            attrs = auth.get_attributes()
            # TODO: update this to correct values or define mapping via settings
            payload = {
                "sub": attrs["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"][0],
                "first_name": attrs["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"][0].split(" ")[0],
                "last_name": attrs["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"][0],
                "email": attrs["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"][0],
            }
            logger.info(f"AUTH ATTRS: {payload}")
            user_info = create_user_if_not_exist(payload)
            logger.info(f"SAML USER INFO: {user_info}")
            # Store session information
            try:
                user_session = get_session_from_user(user_info.user_id)
                logger.info(f"got existing session for user: {user_session}")
            except:
                user_session = None
            try:
                if not user_session or user_session==None:
                        # Create a session ID
                    logger.info("No existing session found...creating new session")
                    session_guid = str(uuid4())
                    session_expiry = datetime.now() + timedelta(minutes=120)
                    user_session = UserSession(
                                            user_id=user_info.user_id,
                                            session_id=session_guid,
                                            session_start=datetime.now(),
                                            session_end=session_expiry
                                            )


                    # ensure session is unique
                    try:
                        get_session_from_session(session_guid)
                        logger.info("No existing session found....saving")
                    except:
                        user_session.save()

                    logger.info(f"Session created with ID: {session_guid} for user: {user_info}")
                else:
                    logger.info(f"user session already exists with session id {user_session.session_id}, {user_session.user_id}")
            except Exception as e:
                logger.error(f"Error saving session to the database: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

            logger.info(f"Redirecting back to client with {req['post_data']['RelayState']}?token=XXX")
            if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
                response = RedirectResponse(url=auth.redirect_to(f"{req['post_data']['RelayState']}/login?token={user_session.session_id}"), status_code=303)
                return response

            return {"user_id": user_session.user_id, "session_id": user_session.session_id}
    else:
        logger.error(f"Errors in SAML response: {errors}")
        raise credentials_exception

@router.post("/validate_token")
async def validate_and_create_session_msal(token: str = Depends(oauth2_scheme)):
    logger.info(f"Received token: {token}")
    if not token or token == None:
        raise credentials_exception
    try:
        # Validate the token
        user_info = verify_token(token)  
        logger.info(f"Token valid for user: {user_info}")
    except HTTPException as e:
        logger.error(f"Token validation error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {e}")
        raise Exception(f"Unexpected token validation exception: {str(e)}")

    if not user_info:
        logger.error("No user info retrieved, token may be invalid")
        raise credentials_exception


    # Store session information
    try:
        user_session = get_session_from_user(user_info.user_id)
        logger.info(f"got existing session for user: {user_session}")
    except:
        user_session = None
    try:
        if not user_session or user_session==None:
                # Create a session ID
            session_guid = str(uuid4())
            session_expiry = datetime.now() + timedelta(minutes=1200)
            user_session = UserSession(
                                    user_id=user_info.user_id,
                                    session_id=session_guid,
                                    session_start=datetime.now(),
                                    session_end=session_expiry
                                    )
            

            # ensure session is unique 
            try:
                existing_session = get_session_from_session(session_guid)
                if existing_session:
                    user_session=existing_session
                    raise Exception('session ID already exists!!')
            except:
                logger.info("saving session")
            finally:
                user_session.save()
                
            logger.info(f"Session created with ID: {session_guid} for user: {user_info.user_id}")
        else: 
            logger.info(f"user session already exists with session id {user_session.session_id}, {user_session.user_id}")
    except Exception as e:
        logger.error(f"Error saving session to the database: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"user_id": user_session.user_id, "session_id": user_session.session_id}

@router.get("/get_generic_token")
def validate_session_no_auth():
    logger.info(f"Received request for generic token for user: {settings.NON_SESSION_ID}")
    try:
        user_session = get_session_from_session(settings.NON_SESSION_ID)
        logger.info(f"got existing session for user: {user_session}")
    except Exception as e:
        logger.error(f"no session found for generic user with error: ", e.__str__())
        user_session = None
        return {"user_id": settings.NON_SESSION_ID, "session_id": settings.NON_SESSION_ID}
    return {"user_id": user_session.user_id, "session_id": user_session.session_id}


def get_session_from_session(session_guid: str):
    current_time = datetime.now()

    session_data = UserSession.objects(session_id=session_guid, session_end__gt=current_time).first()
    logger.info(f"querying session data from db...returning...{session_data}")

    if not session_data or session_data.session_end < current_time:
        message = ''
        if session_data:
            message = f'session expired on {session_data.session_end}'
        else: 
            message = 'no session found'
        raise HTTPException(status_code=401, detail=message)

    return session_data

def get_session_from_user(user_guid: str):

    current_time = datetime.now()
    try:
        logger.info(f"querying user session data for {user_guid}")
        session_data = UserSession.objects(user_id=user_guid, session_end__gt=current_time).first()

        if not session_data or session_data.session_end < current_time:
            logger.info(f"current session is expired...returning none.  session data: {session_data.session_end if session_data else 'no session'}")
            raise HTTPException(status_code=401, detail="Invalid or expired session")

    except Exception as e:
        logger.info(f"no active session found with error: {str(e)}")
        session_data = None

    logger.info(f"querying session data from db...returning...{session_data}")


    return session_data

@router.post("/logout")
async def logout_user(session_guid: str):
    current_time = datetime.now()
    session_data = UserSession.objects(session_id=session_guid).first()

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Invalidate the session by setting its end time to the current time
    session_data.session_end = current_time
    session_data.save()

    return {"message": "User logged out successfully"}
    
# Example of a protected route using this dependency
# @router.post("/protected_route")
# async def protected_route(session_data: UserSession = Depends(get_session_from_user), post_data: dict = Body(...)):


if __name__=="__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InEtMjNmYWxldlpoaEQzaG05Q1Fia1A1TVF5VSJ9.eyJhdWQiOiI4MjhkMzBjOS05NjE5LTRhMTItODYwNC05NmQ0NDY1Mzk1OGYiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vYmI5MzJmMTUtZWYzOC00MmJhLTkxZmMtZjNjNTlkNWRkMWYxL3YyLjAiLCJpYXQiOjE3MTIxODg3MjYsIm5iZiI6MTcxMjE4ODcyNiwiZXhwIjoxNzEyMTk0MzE2LCJhaW8iOiJBWFFBaS84V0FBQUFRS2N0aGwrOUs5dWl3VFpXQzc3VGIxajJYK2V2YVB5WmJWTWhuellteHFOR3hDVTZhN3p1TU42NXZJRER4UTNXWXJxbldhMTIyREVrTzFVRS9iTmZxdWRjbk80U1h0bXlJNEZUWU4zaWlGRitGSWVrelhVK2NDRThpZXRnUy90MFhQeFB2S3lzMXpscFA5cjlzTld2TEE9PSIsImF6cCI6IjgyOGQzMGM5LTk2MTktNGExMi04NjA0LTk2ZDQ0NjUzOTU4ZiIsImF6cGFjciI6IjAiLCJuYW1lIjoiTWFyeSBTY2h3YWJlciBBZG1pbiIsIm9pZCI6IjE1MDY2M2VlLTMyYzYtNGMyYS1iNWUyLTM2ZjVhNmY5MzEyZCIsInByZWZlcnJlZF91c2VybmFtZSI6Im1hMTM3NTY1YWRtaW5AdWNmLmVkdSIsInJoIjoiMC5BUTRBRlMtVHV6anZ1a0tSX1BQRm5WM1I4Y2t3allJWmxoSktoZ1NXMUVaVGxZOE9BQlkuIiwic2NwIjoiVXNlci5SZWFkIiwic3ViIjoiQV9pWEc5TFFqRzg2UFRZMXNnRy1TbTlKTzNJYk1sbGlSa1pvazNCaFQ4SSIsInRpZCI6ImJiOTMyZjE1LWVmMzgtNDJiYS05MWZjLWYzYzU5ZDVkZDFmMSIsInV0aSI6IkJ6ZDJQLVAyT0VXSHQzYXkyNG1PQUEiLCJ2ZXIiOiIyLjAifQ.Lu0OOkz2zf5LEupxnEvzqDAqk0ECadEP8p2_H8Hwt5FbarrKl8h3n2eNSbjktIU16-WjTDFTRg9Qhi67_DaNulOhfqLxIxBwlGLbLVuy3zuqAj216pxDxflB1bEvvVVl1M_6OSqSIy_ZZsaR5IkeI-osqtzXDznHGjL8Ucz7epDUpiyOFlM5chkAyNEl2qn3CBieJPCGIHuwaK1Gsm-5YfgGYbpUzXpy05WW-3aPH_ViX92n_mSx4HS_35FDbC8DB8YNp2cjzDnle_Usx-WUTBKbYr3-usoD3lUI84TGCASSVsCOER20hECnMudEKwiR3YcsF-RocTlx82hsFXEDhQ"
    loop.run_until_complete(validate_and_create_session_msal(token))

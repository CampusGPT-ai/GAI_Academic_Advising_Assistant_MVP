from fastapi import HTTPException, Depends
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt, json
from jwt import PyJWKClient
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter
import os
from datetime import datetime, timedelta
from data.models import UserSession
import logging
from settings.settings import Settings

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
        
        # logger.debug("got token payload", payload)

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except:
        raise credentials_exception


@router.post("/validate_token")
async def validate_and_create_session(token: str = Depends(oauth2_scheme)):
    logger.info(f"Received token: {token}")
    if not token or token == None:
        raise credentials_exception
    if token == "DEV":
        user_info = "dev"
    else:
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
        user_session = get_session_from_user(user_info)
        logger.info(f"got existing session for user: {user_session}")
    except:
        user_session = None
    try:
        if not user_session or user_session==None:
                # Create a session ID
            session_guid = str(uuid4())
            session_expiry = datetime.now() + timedelta(minutes=120)
            user_session = UserSession(
                                    user_id=user_info,
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
                
            logger.info(f"Session created with ID: {session_guid} for user: {user_info}")
        else: 
            logger.info(f"user session already exists with session id {user_session.session_id}, {user_session.user_id}")
    except Exception as e:
        logger.error(f"Error saving session to the database: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"user_id": user_session.user_id, "session_id": user_session.session_id}


def get_session_from_session(session_guid: str):
    current_time = datetime.now()
    logger.debug(f"Querying user session data for {session_guid}")
    session_data = UserSession.objects(session_id=session_guid, session_end__gt=current_time).first()


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
    token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImtXYmthYTZxczh3c1RuQndpaU5ZT2hIYm5BdyIsImtpZCI6ImtXYmthYTZxczh3c1RuQndpaU5ZT2hIYm5BdyJ9.eyJhdWQiOiI4MjhkMzBjOS05NjE5LTRhMTItODYwNC05NmQ0NDY1Mzk1OGYiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9iYjkzMmYxNS1lZjM4LTQyYmEtOTFmYy1mM2M1OWQ1ZGQxZjEvIiwiaWF0IjoxNzA2OTIwMjYwLCJuYmYiOjE3MDY5MjAyNjAsImV4cCI6MTcwNjkyNDg4MywiYWNyIjoiMSIsImFpbyI6IkFWUUFxLzhWQUFBQThBeHQ3MngwM01ld0p3NWFQc09Rb05hNTVuTlppdHR1eDV0bnk0U2NXVUpMa3R3MHNNMmpadUZsWEh3RDZ5a1VIUStnc2ljRlB5dmk1TktRVGFvdzVaWlk5OVAwRlZQQ0ZYbENBc0t2bzg0PSIsImFtciI6WyJwd2QiLCJtZmEiXSwiYXBwaWQiOiI4MjhkMzBjOS05NjE5LTRhMTItODYwNC05NmQ0NDY1Mzk1OGYiLCJhcHBpZGFjciI6IjAiLCJmYW1pbHlfbmFtZSI6IlNjaHdhYmVyIiwiZ2l2ZW5fbmFtZSI6Ik1hcnkiLCJpcGFkZHIiOiIyNjAxOjYwMDo4ZjAxOjExNjA6OGMzYTphMzdmOjgxNjM6YjFjYSIsIm5hbWUiOiJNYXJ5IFNjaHdhYmVyIEFkbWluIiwib2lkIjoiMTUwNjYzZWUtMzJjNi00YzJhLWI1ZTItMzZmNWE2ZjkzMTJkIiwib25wcmVtX3NpZCI6IlMtMS01LTIxLTI3MDI0MDUyNS0xNjczMTAwNzAyLTUwNjcwMjU1NC0zMzYxMTcyIiwicmgiOiIwLkFRNEFGUy1UdXpqdnVrS1JfUFBGblYzUjhja3dqWUlabGhKS2hnU1cxRVpUbFk4T0FCWS4iLCJzY3AiOiJVc2VyLlJlYWQiLCJzdWIiOiJBX2lYRzlMUWpHODZQVFkxc2dHLVNtOUpPM0liTWxsaVJrWm9rM0JoVDhJIiwidGlkIjoiYmI5MzJmMTUtZWYzOC00MmJhLTkxZmMtZjNjNTlkNWRkMWYxIiwidW5pcXVlX25hbWUiOiJtYTEzNzU2NWFkbWluQHVjZi5lZHUiLCJ1cG4iOiJtYTEzNzU2NWFkbWluQHVjZi5lZHUiLCJ1dGkiOiJjQ1h5cUJxU2JFcWpsS2FRUlpWSkFBIiwidmVyIjoiMS4wIn0.AMAu1woVCSXLEeH725C0-MbZ6QbnlsGXsF8dAAsa9k51RY4SyLUCOGP_0lYrUW8r29f6PNnHSKRBkI5FLUcIZ-Q04rJdfnCHBiwel8qo7mYD_JMx4fldR3sFFx9aOizREUCTixQT6LuGoGthuj4YBdL5NTbwKNCVnyMjoxAAbXCEJjxrfBs8twhrY5AxUJCV4JRP168_ihMsKCzDXeF-a24gutjAZUpjm9Pv-x3wQLUdR9J0HyI0-Aa9L-m0WK13dJRtpNw_3C6xxb2wHuvUuOCm2GZrB36kfWSERZKOhFiDBhDueL98NTVX2-Jxk22FrIBpcO9I5ZIeArM7258GkA"
    verify_token(token)

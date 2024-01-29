from fastapi import HTTPException, Depends
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWKClient
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter
import os
from datetime import datetime, timedelta
from data.models import UserSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

from fastapi.responses import JSONResponse


CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)) -> Optional[str]:
    issuer_url = f"https://sts.windows.net/{TENANT_ID}/"
    jwks_client = PyJWKClient(f"{issuer_url}/discovery/keys")
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
        
        # print("got token payload", payload)

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.post("/validate_token")
async def validate_and_create_session(token: str = Depends(oauth2_scheme)):
    logger.info(f"Received token: {token}")
    try:
        # Validate the token
        user_info = verify_token(token)  # Implement this function'
        logger.info(f"Token valid for user: {user_info}")
    except HTTPException as e:
        logger.error(f"Token validation error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {e}")
        raise credentials_exception

    if not user_info:
        logger.error("No user info retrieved, token may be invalid")
        raise credentials_exception


    # Store session information
    user_session = get_session_from_user(user_info)
    try:
        if not user_session:
                # Create a session ID
            session_guid = str(uuid4())
            session_expiry = datetime.now() + timedelta(minutes=120)
            user_session = UserSession(
                                    user_id=user_info,
                                    session_id=session_guid,
                                    session_start=datetime.now(),
                                    session_end=session_expiry
                                    )
            user_session.save()
            logger.info(f"Session created with ID: {session_guid} for user: {user_info}")
        else: 
            logger.info(f"user session already exists with session id {user_session.session_id}, {user_session.user_id}")
    except Exception as e:
        logger.error(f"Error saving session to the database: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"session_id": user_session.session_id}


def get_session_from_session(session_guid: str):
    current_time = datetime.now()
    session_data = UserSession.objects(session_id=session_guid).first()


    if not session_data or session_data.session_end < current_time:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session_data

def get_session_from_user(user_guid: str):
    current_time = datetime.now()
    session_data = UserSession.objects(user_id=user_guid).first()


    if not session_data or session_data.session_end < current_time:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

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
# @router.get("/protected_route")
# async def protected_route(user_info: str = Depends(get_session_from_user)):
#   return {"message": "Access to protected data", "user_info": user_info}



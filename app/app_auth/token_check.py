from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv
from fastapi import HTTPException
import requests
from msal import ConfidentialClientApplication
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from cryptography.hazmat.primitives import serialization
import jwt
from jwt import PyJWKClient
from settings.settings import Settings
from data.models import Profile
from datetime import datetime
settings = Settings()
load_dotenv()

# Environment Variables
CLIENT_ID = settings.AZURE_CLIENT_ID
TENANT_ID = settings.AZURE_TENANT_ID
CLIENT_SECRET = settings.AZURE_CLIENT_SECRET
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = [f"{CLIENT_ID}/.default"]  # Use a more appropriate scope for client credentials flow

# The issuer URL & audience from your Azure app registration
issuer_url = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
# MSAL Confidential Client Application
app_confidence = ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

# Test Function for Acquiring Token
def test_acquire_token():
    result = app_confidence.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        print("Token acquired successfully.")
        print("Access Token:", result['access_token'])
        return result['access_token']
        # Additional validation or actions can be added here
    else:
        print("Failed to acquire token.")
        print("Error details:", result.get("error_description"))
        
def verify_token(token):
    jwks_client = PyJWKClient(f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys")
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    payload = jwt.decode(
        token, 
        signing_key.key, 
        algorithms=["RS256"], 
        audience=CLIENT_ID, 
        issuer=issuer_url,
        options={"verify_signature": True, "verify_aud": True, "verify_iss": True}
    )

    return payload

def test_create_user(payload):
    from settings.settings import Settings
    from mongoengine import connect
    settings = Settings()
    db_name = settings.MONGO_DB
    db_conn = settings.MONGO_CONN_STR
    _mongo_conn = connect(db=db_name, host=db_conn)
    try:
        user_id: str = payload.get("sub")
        first_name: str = payload.get("first_name")
        last_name: str = payload.get("last_name")
        email: str = payload.get("email")
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
    return user_id


# Run the test
if __name__ == "__main__":

    token = test_acquire_token()

    payload = verify_token(token)
    test_create_user(payload)

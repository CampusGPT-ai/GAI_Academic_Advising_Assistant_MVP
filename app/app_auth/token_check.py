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

load_dotenv()

# Environment Variables
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = [f"{CLIENT_ID}/.default"]  # Use a more appropriate scope for client credentials flow

# The issuer URL & audience from your Azure app registration
issuer_url = f"https://sts.windows.net/{TENANT_ID}/"

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
    jwks_client = PyJWKClient(f"{issuer_url}/discovery/keys")
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    decoded_token = jwt.decode(
        token, 
        signing_key.key, 
        algorithms=["RS256"], 
        audience=CLIENT_ID, 
        issuer=issuer_url,
        options={"verify_signature": True, "verify_aud": True, "verify_iss": True}
    )

    print(decoded_token)


# Run the test
if __name__ == "__main__":
    token = test_acquire_token()
    verify_token(token)

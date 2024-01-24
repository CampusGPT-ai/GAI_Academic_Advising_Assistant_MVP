from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from msal import ConfidentialClientApplication
from starlette.middleware.sessions import SessionMiddleware
import os
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("VERY_SECRET_KEY"))

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read"]  # Add other scopes as needed
REDIRECT_PATH = "/getAToken"  # The endpoint in your application for receiving the code
oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl=f"{AUTHORITY}/oauth2/v2.0/authorize", tokenUrl=f"{AUTHORITY}/oauth2/v2.0/token")

def build_msal_app():
    return ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )

def get_auth_url(request: Request):
    app = build_msal_app()
    auth_url, state = app.get_authorization_request_url(SCOPE, redirect_uri=request.url_for("authorized"))
    request.session["state"] = state  # Saving the state for validation later
    return auth_url

@app.get("/login")
async def login(request: Request):
    auth_url = get_auth_url(request)
    return RedirectResponse(auth_url)

@app.get(REDIRECT_PATH)
async def authorized(request: Request, code: str = Depends(oauth2_scheme)):
    state = request.session.get("state")
    if request.query_params.get('state') != state:
        raise HTTPException(status_code=400, detail="State does not match")
    app = build_msal_app()
    result = app.acquire_token_by_authorization_code(
        code, 
        scopes=SCOPE, 
        redirect_uri=request.url_for("authorized")
    )
    if "access_token" in result:
        # Successful authentication
        # Use this access token to call the API or access resources
        return "Logged in successfully"
    else:
        # Handle error
        return HTTPException(status_code=500, detail="Authentication failed")

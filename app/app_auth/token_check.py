from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv

load_dotenv()

# Environment Variables
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]  # Use a more appropriate scope for client credentials flow

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
        # Additional validation or actions can be added here
    else:
        print("Failed to acquire token.")
        print("Error details:", result.get("error_description"))

# Run the test
if __name__ == "__main__":
    test_acquire_token()

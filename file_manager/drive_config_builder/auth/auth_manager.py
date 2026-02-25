import base64
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_authenticated_drive_service():
    """
    Authenticates with Google Drive using a Google Service Account
    and returns an authorized Drive API service client.

    Authentication Flow:
        - Reads the Base64-encoded service account JSON from the
          GOOGLE_SERVICE_ACCOUNT_B64 environment variable.
        - Decodes and loads the credentials into memory.
        - Builds an authenticated Drive v3 service instance.

    Requirements:
        - GOOGLE_SERVICE_ACCOUNT_B64 must be set in the environment.
        - The service account must have access to the target Drive folder
          (shared explicitly with the service account email).
    """
    b64_credentials = os.environ["GOOGLE_SERVICE_ACCOUNT_B64"]
    decoded_json = base64.b64decode(b64_credentials).decode("utf-8")
    credentials_info = json.loads(decoded_json)

    creds = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES,
    )
    
    service = build("drive", "v3", credentials= creds)
    print("Google Drive authentication successful.")
    return service

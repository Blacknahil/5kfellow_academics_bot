import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SAVED_TOKEN_PATH = "token.json"
GOOGLE_CREDENTIALS_PATH = "credentials.json"

def get_authenticated_drive_service():
    """
    Authenticates with Google Drive and returns a service client.
    Handles token saving and refreshing automatically.
    
    Requires:
        - credentials.json  (OAuth client ID from Google Cloud)
    Produces:
        - token.json        (saved automatically after first login)
    """
    creds = None
    if os.path.exists(SAVED_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(SAVED_TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print("Error during authentication:", e)
                raise e
        
        with open(SAVED_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    
    service = build("drive", "v3", credentials= creds )
    print("Google Drive authentication successful.")
    return service

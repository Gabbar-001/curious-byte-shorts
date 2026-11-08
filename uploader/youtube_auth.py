"""
YouTube OAuth Authentication Manager.
Handles initial browser-based sign-in and token persistence for YouTube Data API v3.
"""

import os
import sys
import pickle

# Force UTF-8 stdout
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "client_secrets.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "token.json")

def get_authenticated_service():
    """
    Authenticates and returns the YouTube API credentials.
    If token.json exists and is valid, loads it.
    Otherwise initiates OAuth browser flow using client_secrets.json.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[YouTubeAuth] Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print("\n" + "="*60)
                print("  YOUTUBE API CREDENTIALS NOT FOUND")
                print("="*60)
                print(f"Please place your Google OAuth client secrets file at:")
                print(f"  {os.path.abspath(CLIENT_SECRETS_FILE)}")
                print("\nSteps to get it:")
                print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                print("2. Create a project and enable 'YouTube Data API v3'")
                print("3. Go to Credentials -> Create Credentials -> OAuth client ID (Desktop app)")
                print("4. Download the JSON file and rename it to 'client_secrets.json'")
                print("5. Place it in the 'config' folder.")
                print("="*60 + "\n")
                return None

            print("[YouTubeAuth] Initiating browser login for YouTube...", flush=True)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')

        # Save credentials for future unattended runs
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
        print(f"[YouTubeAuth] Credentials saved to {TOKEN_FILE}")

    return creds

if __name__ == "__main__":
    creds = get_authenticated_service()
    if creds:
        print("YouTube Authentication verified!")
    else:
        print("Setup needed for YouTube credentials.")

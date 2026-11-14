"""
YouTube OAuth Authentication Manager.
Handles initial browser-based sign-in and token persistence for YouTube Data API v3.
"""

import os
import sys
import json
import subprocess
import webbrowser

# Force UTF-8 stdout
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube"
]

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "client_secrets.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "token.json")
AUTH_URL_FILE = os.path.join(os.path.dirname(__file__), "..", "output", "auth_url.txt")

def update_github_secrets_export(token_path):
    """Updates github_secrets_to_copy.txt with latest token JSON for GitHub Actions."""
    try:
        if not os.path.exists(token_path):
            return
        with open(token_path, "r", encoding="utf-8") as f:
            token_content = f.read().strip()
        export_file = os.path.join(os.path.dirname(__file__), "..", "github_secrets_to_copy.txt")
        env_file = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
        gemini_key = ""
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as ef:
                for line in ef:
                    if line.startswith("GEMINI_API_KEY="):
                        gemini_key = line.strip().split("=", 1)[1]
        with open(export_file, "w", encoding="utf-8") as out:
            out.write("="*60 + "\n")
            out.write("  LATEST GITHUB ACTIONS SECRETS (UPDATED)\n")
            out.write("="*60 + "\n\n")
            out.write("1. Secret Name: YOUTUBE_TOKEN_JSON\n")
            out.write("   Secret Value:\n")
            out.write(token_content + "\n\n")
            if gemini_key:
                out.write("2. Secret Name: GEMINI_API_KEY\n")
                out.write("   Secret Value:\n")
                out.write(gemini_key + "\n\n")
        print("[YouTubeAuth] Updated github_secrets_to_copy.txt with fresh credentials.")
    except Exception as e:
        print(f"[YouTubeAuth] Could not update secrets export file: {e}")

def get_authenticated_service():
    """
    Authenticates and returns the YouTube API credentials.
    If token.json exists and is valid with proper scopes, loads it.
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
            try:
                print("[YouTubeAuth] Refreshing expired credentials...", flush=True)
                creds.refresh(Request())
            except Exception as e:
                print(f"[YouTubeAuth] Refresh token failed or revoked ({e}).", flush=True)
                print("[YouTubeAuth] Initiating fresh browser authentication...", flush=True)
                creds = None

        if not creds or not creds.valid:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print("\n" + "="*60, flush=True)
                print("  YOUTUBE API CREDENTIALS NOT FOUND", flush=True)
                print("="*60, flush=True)
                print(f"Please place your Google OAuth client secrets file at:", flush=True)
                print(f"  {os.path.abspath(CLIENT_SECRETS_FILE)}", flush=True)
                print("="*60 + "\n", flush=True)
                return None

            print("[YouTubeAuth] Initializing OAuth authentication flow...", flush=True)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            flow.redirect_uri = "http://localhost:8080/"
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

            # Save URL to file so user or automated tools can read it
            os.makedirs(os.path.dirname(AUTH_URL_FILE), exist_ok=True)
            with open(AUTH_URL_FILE, "w", encoding="utf-8") as f:
                f.write(auth_url)

            print("\n" + "="*70, flush=True)
            print("  GOOGLE OAUTH BROWSER LOGIN REQUIRED", flush=True)
            print("="*70, flush=True)
            print(f"Auth URL: {auth_url}\n", flush=True)
            print("Opening browser for authorization...", flush=True)
            print("="*70 + "\n", flush=True)

            # Attempt to launch the default browser in Windows session
            try:
                subprocess.Popen(["powershell", "-NoProfile", "-Command", f"Start-Process '{auth_url}'"])
            except Exception:
                webbrowser.open(auth_url)

            # Listen on port 8080 for the OAuth callback
            creds = flow.run_local_server(
                port=8080,
                prompt='consent',
                access_type='offline',
                open_browser=False
            )

        # Save credentials for future unattended runs
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
        print(f"[YouTubeAuth] Credentials saved to {TOKEN_FILE}", flush=True)
        update_github_secrets_export(TOKEN_FILE)

        # Automatically push fresh token directly to GitHub Secrets using GITHUB_TOKEN
        try:
            from sync_github_secrets import sync_all_secrets
            sync_all_secrets()
        except Exception as e:
            print(f"[YouTubeAuth] Note on syncing secrets to GitHub: {e}", flush=True)

    return creds

if __name__ == "__main__":
    creds = get_authenticated_service()
    if creds:
        print("[YouTubeAuth] YouTube Authentication verified and active!", flush=True)
    else:
        print("[YouTubeAuth] Setup needed for YouTube credentials.", flush=True)

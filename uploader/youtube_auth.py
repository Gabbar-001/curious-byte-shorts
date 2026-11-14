"""
YouTube OAuth Authentication Manager.
Handles initial browser-based sign-in and token persistence for YouTube Data API v3.
Features zero-dependency foolproof HTTP server callback and automatic GitHub secrets sync.
"""

import os
import sys
import json
import time
import subprocess
import webbrowser
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

# Force UTF-8 stdout
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

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

_AUTH_CODE = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _AUTH_CODE
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _AUTH_CODE = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>Authorization Successful</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #58a6ff; text-align: center; padding: 60px;">
                <h1 style="color: #3fb950; font-size: 32px;">Authorization Successful!</h1>
                <p style="color: #c9d1d9; font-size: 18px;">Curious Byte YouTube access has been successfully granted.</p>
                <p style="color: #8b949e; font-size: 14px;">Credentials have been saved and synchronized. You can safely close this browser window.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            err_msg = params.get("error", ["Unknown error"])[0]
            self.wfile.write(f"<h1>Authorization Error</h1><p>{err_msg}</p>".encode("utf-8"))

    def log_message(self, format, *args):
        pass  # Suppress default server logs for clean stdout

def exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8080/"):
    """Exchanges an authorization code for access and refresh tokens."""
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def update_github_secrets_export(token_path):
    """Updates github_secrets_to_copy.txt and triggers direct API sync."""
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
        print("[YouTubeAuth] Updated github_secrets_to_copy.txt with fresh credentials.", flush=True)

        try:
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            from sync_github_secrets import sync_all_secrets
            sync_all_secrets()
        except Exception as se:
            print(f"[YouTubeAuth] Direct GitHub API sync note: {se}", flush=True)

    except Exception as e:
        print(f"[YouTubeAuth] Could not update secrets export file: {e}", flush=True)

def get_authenticated_service():
    """
    Authenticates and returns the YouTube API credentials.
    If token.json exists and is valid with proper scopes, loads it.
    Otherwise initiates OAuth browser flow using client_secrets.json.
    """
    global _AUTH_CODE
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
                print(f"Error: {CLIENT_SECRETS_FILE} not found.", flush=True)
                return None

            with open(CLIENT_SECRETS_FILE, "r", encoding="utf-8") as cs_f:
                cs_data = json.load(cs_f)
            installed = cs_data.get("installed") or cs_data.get("web", {})
            client_id = installed.get("client_id")
            client_secret = installed.get("client_secret")

            redirect_uri = "http://localhost:8080/"
            scope_param = "+".join(urllib.parse.quote(s, safe="") for s in SCOPES)
            auth_url = (
                f"https://accounts.google.com/o/oauth2/auth?"
                f"response_type=code&"
                f"client_id={client_id}&"
                f"redirect_uri={urllib.parse.quote(redirect_uri, safe='')}&"
                f"scope={scope_param}&"
                f"prompt=consent&"
                f"access_type=offline"
            )

            # Persist URL to output/auth_url.txt
            os.makedirs(os.path.dirname(AUTH_URL_FILE), exist_ok=True)
            with open(AUTH_URL_FILE, "w", encoding="utf-8") as f:
                f.write(auth_url)

            print("\n" + "="*70, flush=True)
            print("  GOOGLE OAUTH BROWSER LOGIN REQUIRED", flush=True)
            print("="*70, flush=True)
            print(f"Auth URL: {auth_url}\n", flush=True)
            print("Opening browser for authorization...", flush=True)
            print("="*70 + "\n", flush=True)

            try:
                subprocess.Popen(["powershell", "-NoProfile", "-Command", f"Start-Process '{auth_url}'"])
            except Exception:
                webbrowser.open(auth_url)

            # Start local server to receive the authorization code
            server_address = ("localhost", 8080)
            httpd = HTTPServer(server_address, OAuthCallbackHandler)
            print("[YouTubeAuth] Listening on http://localhost:8080/ for OAuth callback...", flush=True)

            while _AUTH_CODE is None:
                httpd.handle_request()

            httpd.server_close()
            print("[YouTubeAuth] Authorization code captured! Exchanging for tokens...", flush=True)

            token_response = exchange_code_for_token(_AUTH_CODE, client_id, client_secret, redirect_uri)
            access_token = token_response.get("access_token")
            refresh_token = token_response.get("refresh_token")
            expires_in = token_response.get("expires_in", 3600)

            now = datetime.now(timezone.utc)
            expiry = (now + timedelta(seconds=expires_in)).isoformat().replace("+00:00", "Z")

            token_data = {
                "token": access_token,
                "refresh_token": refresh_token,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": client_id,
                "client_secret": client_secret,
                "scopes": SCOPES,
                "universe_domain": "googleapis.com",
                "account": "",
                "expiry": expiry
            }

            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, "w", encoding="utf-8") as tf:
                json.dump(token_data, tf, indent=2)
            print(f"[YouTubeAuth] Credentials successfully saved to {TOKEN_FILE}", flush=True)

            update_github_secrets_export(TOKEN_FILE)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    return creds

if __name__ == "__main__":
    creds = get_authenticated_service()
    if creds:
        print("[YouTubeAuth] YouTube Authentication verified and active!", flush=True)
    else:
        print("[YouTubeAuth] Setup needed for YouTube credentials.", flush=True)

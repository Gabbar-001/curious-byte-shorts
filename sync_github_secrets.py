"""
Automatically uploads local secrets to GitHub Actions Secrets via GitHub REST API and PyNaCl.
"""
import os
import json
import base64
import urllib.request
from nacl import encoding, public
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "config", ".env"))

OWNER = "Gabbar-001"
REPO = "curious-byte-shorts"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_public_key():
    req = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/public-key",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Antigravity"
        }
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def encrypt_secret(public_key_str: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_github_secret(secret_name: str, secret_value: str):
    if not GITHUB_TOKEN:
        print("[GitHubSync] GITHUB_TOKEN not found.")
        return False

    key_data = get_public_key()
    encrypted_value = encrypt_secret(key_data["key"], secret_value)

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/{secret_name}"
    payload = json.dumps({
        "encrypted_value": encrypted_value,
        "key_id": key_data["key_id"]
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="PUT",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Antigravity"
        }
    )
    with urllib.request.urlopen(req) as response:
        if response.status in (201, 204):
            print(f"[GitHubSync] Successfully synced secret '{secret_name}' to GitHub Actions!")
            return True
        else:
            print(f"[GitHubSync] Status {response.status} when syncing '{secret_name}'")
            return False

def sync_all_secrets():
    token_path = os.path.join(os.path.dirname(__file__), "config", "token.json")
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            token_b64 = base64.b64encode(f.read()).decode("utf-8")
        set_github_secret("YOUTUBE_TOKEN_BASE64", token_b64)

if __name__ == "__main__":
    sync_all_secrets()

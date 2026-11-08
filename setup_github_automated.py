"""
Fully Automated GitHub Setup Script for Curious Byte Engine.
Uses a GitHub Personal Access Token to:
1. Verify GitHub account credentials
2. Create the private GitHub repository automatically
3. Encrypt and upload all 3 repository secrets (GEMINI_API_KEY, YOUTUBE_TOKEN_BASE64, CLIENT_SECRETS_BASE64)
4. Push all code to the 'main' branch
5. Sanitize local git remote configuration
"""

import os
import sys
import base64
import subprocess
import requests
from dotenv import dotenv_values
from nacl import encoding, public

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    """Encrypts a secret using the GitHub repository public key (NaCl SealedBox)."""
    public_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def setup_github(token: str, repo_name: str = "curious-byte-shorts"):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CuriousByteEngine"
    }

    print("\n" + "=" * 65)
    print("  🚀 AUTOMATED GITHUB REPOSITORY & SECRETS SETUP")
    print("=" * 65)

    # 1. Verify User Credentials
    print("[1/5] Verifying GitHub Token...")
    res = requests.get("https://api.github.com/user", headers=headers)
    if res.status_code != 200:
        print(f"❌ Authentication Failed: HTTP {res.status_code}")
        print(res.json().get("message", "Invalid token"))
        return False

    user_data = res.json()
    username = user_data["login"]
    print(f"  ✓ Authenticated as: {username} ({user_data.get('name', username)})")

    # 2. Create or verify private repository
    print(f"\n[2/5] Creating private repository: {username}/{repo_name}...")
    repo_check = requests.get(f"https://api.github.com/repos/{username}/{repo_name}", headers=headers)
    if repo_check.status_code == 200:
        print(f"  ✓ Repository '{repo_name}' already exists.")
    else:
        create_payload = {
            "name": repo_name,
            "description": "Autonomous YouTube Shorts Engine with GitHub Actions Cloud Scheduler",
            "private": True,
            "auto_init": False
        }
        create_res = requests.post("https://api.github.com/user/repos", headers=headers, json=create_payload)
        if create_res.status_code in [201, 200]:
            print(f"  ✓ Private repository '{username}/{repo_name}' successfully created!")
        else:
            print(f"❌ Failed to create repository: HTTP {create_res.status_code}")
            print(create_res.json())
            return False

    # 3. Retrieve Repository Public Key for Secrets
    print("\n[3/5] Fetching repository encryption key...")
    pk_res = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/actions/secrets/public-key", headers=headers)
    if pk_res.status_code != 200:
        print(f"❌ Failed to retrieve public key: HTTP {pk_res.status_code}")
        print(pk_res.json())
        return False

    pk_data = pk_res.json()
    key_id = pk_data["key_id"]
    public_key_b64 = pk_data["key"]
    print(f"  ✓ Key retrieved (Key ID: {key_id})")

    # 4. Prepare & Upload Secrets
    print("\n[4/5] Encrypting and uploading 3 Cloud Secrets to GitHub Actions...")
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    env_vars = dotenv_values(os.path.join(config_dir, ".env"))
    gemini_key = env_vars.get("GEMINI_API_KEY", "")

    with open(os.path.join(config_dir, "token.json"), "rb") as f:
        token_b64 = base64.b64encode(f.read()).decode("utf-8")

    with open(os.path.join(config_dir, "client_secrets.json"), "rb") as f:
        secrets_b64 = base64.b64encode(f.read()).decode("utf-8")

    secrets_dict = {
        "GEMINI_API_KEY": gemini_key,
        "YOUTUBE_TOKEN_BASE64": token_b64,
        "CLIENT_SECRETS_BASE64": secrets_b64
    }

    for s_name, s_val in secrets_dict.items():
        enc_val = encrypt_secret(public_key_b64, s_val)
        sec_payload = {
            "encrypted_value": enc_val,
            "key_id": key_id
        }
        sec_res = requests.put(
            f"https://api.github.com/repos/{username}/{repo_name}/actions/secrets/{s_name}",
            headers=headers,
            json=sec_payload
        )
        if sec_res.status_code in [201, 204]:
            print(f"  ✓ Secret '{s_name}' configured successfully.")
        else:
            print(f"  ⚠️ Error setting secret '{s_name}': HTTP {sec_res.status_code}")
            print(sec_res.text)

    # 5. Push Code via Git
    print("\n[5/5] Pushing local codebase to GitHub...")
    auth_remote = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    clean_remote = f"https://github.com/{username}/{repo_name}.git"

    # Check existing remote
    remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout.strip().split()
    if "origin" in remotes:
        subprocess.run(["git", "remote", "set-url", "origin", auth_remote], check=True)
    else:
        subprocess.run(["git", "remote", "add", "origin", auth_remote], check=True)

    push_res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], capture_output=True, text=True)
    if push_res.returncode != 0:
        print(f"❌ Git push failed:\n{push_res.stderr}")
        return False
    print("  ✓ Code successfully pushed to 'main' branch!")

    # Sanitize remote URL to remove token
    subprocess.run(["git", "remote", "set-url", "origin", clean_remote], check=True)
    print("  ✓ Local git remote sanitized (credentials stripped).")

    print("\n" + "=" * 65)
    print("  🎉 COMPLETE GITHUB AUTOMATION SUCCESS!")
    print(f"  • Repository: https://github.com/{username}/{repo_name}")
    print(f"  • Actions Tab: https://github.com/{username}/{repo_name}/actions")
    print("=" * 65)
    print("\nYour cloud engine is now LIVE. It will run daily at 11:55 PM IST,")
    print("and you can trigger batches right from your phone anytime!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token_arg = sys.argv[1].strip()
    else:
        token_arg = input("Enter your GitHub Personal Access Token (starts with ghp_): ").strip()
    
    if not token_arg:
        print("❌ No token provided. Exiting.")
        sys.exit(1)
        
    setup_github(token_arg)

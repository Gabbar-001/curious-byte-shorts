"""
Helper to export GitHub Repository Secrets for Curious Byte Engine.
Reads your existing local credentials and generates the 3 secrets needed in GitHub.
Saves them into github_secrets_to_copy.txt (which is ignored by Git).
"""

import os
import sys
import base64
from dotenv import dotenv_values

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
ENV_FILE = os.path.join(CONFIG_DIR, ".env")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token.json")
SECRETS_FILE = os.path.join(CONFIG_DIR, "client_secrets.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "github_secrets_to_copy.txt")

def main():
    print("=" * 65)
    print("  🔑 CURIOUS BYTE — GITHUB SECRETS EXPORTER")
    print("=" * 65)

    env_vars = dotenv_values(ENV_FILE)
    gemini_key = env_vars.get("GEMINI_API_KEY", "")

    if not os.path.exists(TOKEN_FILE):
        print(f"❌ Error: {TOKEN_FILE} not found!")
        return
    if not os.path.exists(SECRETS_FILE):
        print(f"❌ Error: {SECRETS_FILE} not found!")
        return

    with open(TOKEN_FILE, "rb") as f:
        token_b64 = base64.b64encode(f.read()).decode("utf-8")

    with open(SECRETS_FILE, "rb") as f:
        secrets_b64 = base64.b64encode(f.read()).decode("utf-8")

    out_content = f"""================================================================================
GITHUB REPOSITORY SECRETS FOR CURIOUS BYTE ENGINE
Repository: Your GitHub Private Repository -> Settings -> Secrets and variables -> Actions
================================================================================

--- SECRET 1 ---
Name:  GEMINI_API_KEY
Value:
{gemini_key}

--- SECRET 2 ---
Name:  YOUTUBE_TOKEN_BASE64
Value:
{token_b64}

--- SECRET 3 ---
Name:  CLIENT_SECRETS_BASE64
Value:
{secrets_b64}

================================================================================
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(out_content)

    print(f"\n✅ All 3 Secrets successfully generated and saved to:")
    print(f"   📁 {os.path.abspath(OUTPUT_FILE)}")
    print("\nYou can open this file and copy each secret directly into GitHub.")
    print("=" * 65)

if __name__ == "__main__":
    main()

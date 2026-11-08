"""
Curious Byte Unique — Mobile Telegram Controller.
Enables full management and execution of the YouTube Shorts pipeline from any mobile phone:
- Commands:
    /start     - Welcome menu and command list
    /run       - Trigger generation of daily batch (e.g. /run 48)
    /status    - View upcoming scheduled videos and channel status
    /history   - View recently uploaded Shorts and live YouTube links
    /stop      - Gracefully stop any active pipeline task
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

CURRENT_PROCESS = None

def send_telegram_message(text: str, chat_id: str = None, parse_mode: str = "HTML"):
    if not API_BASE:
        print("[TelegramController] Error: TELEGRAM_BOT_TOKEN is not set.")
        return
    cid = chat_id or ALLOWED_CHAT_ID
    if not cid:
        return

    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": cid,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[TelegramController] Failed to send message: {e}")

def send_telegram_photo(photo_path: str, caption: str = "", chat_id: str = None):
    if not API_BASE or not os.path.exists(photo_path):
        return
    cid = chat_id or ALLOWED_CHAT_ID
    url = f"{API_BASE}/sendPhoto"
    try:
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": cid, "caption": caption, "parse_mode": "HTML"}
            requests.post(url, files=files, data=data, timeout=15)
    except Exception as e:
        print(f"[TelegramController] Failed to send photo: {e}")

def get_latest_status():
    history_file = os.path.join(os.path.dirname(__file__), "..", "output", "uploads_history.json")
    if not os.path.exists(history_file):
        return "No upload history found yet."

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception as e:
        return f"Error reading upload history: {e}"

    if not records:
        return "Upload history is currently empty."

    total_uploads = len(records)
    recent = records[-5:]

    msg = f"<b>📊 Curious Byte YouTube Status</b>\n"
    msg += f"• Total Uploads in Channel History: <b>{total_uploads}</b>\n\n"
    msg += f"<b>🎬 Last 5 Uploaded/Scheduled Shorts:</b>\n"
    for r in recent:
        title = r.get("title", "Short")
        url = r.get("url", "https://youtu.be/" + r.get("video_id", ""))
        sched = r.get("scheduled_publish_at", "Immediate")
        msg += f"• <a href='{url}'>{title}</a>\n  ⏰ <i>{sched}</i>\n"

    return msg

def run_scheduler_async(count: int = 48, start_at: str = "midnight"):
    global CURRENT_PROCESS
    if CURRENT_PROCESS and CURRENT_PROCESS.poll() is None:
        return False, "A batch generation is already running right now!"

    script_path = os.path.join(os.path.dirname(__file__), "..", "run_autonomous_scheduler.py")
    cmd = [sys.executable, script_path, "--count", str(count), "--start-at", start_at]

    try:
        CURRENT_PROCESS = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, f"🚀 Autonomous Pipeline started for {count} Shorts (Start: {start_at})!"
    except Exception as e:
        return False, f"Failed to launch pipeline: {e}"

def handle_command(text: str, chat_id: str):
    cmd_parts = text.strip().split()
    cmd = cmd_parts[0].lower() if cmd_parts else ""

    if cmd in ["/start", "/help"]:
        msg = (
            "<b>👋 Welcome to Curious Byte Mobile Controller!</b>\n\n"
            "You can control your entire YouTube Shorts engine from this chat.\n\n"
            "<b>Commands:</b>\n"
            "▶️ <code>/run [count]</code> - Start generating & scheduling Shorts (e.g. <code>/run 48</code>)\n"
            "📊 <code>/status</code> - View current upload counts and scheduled release queue\n"
            "📜 <code>/history</code> - View recent video links\n"
            "🛑 <code>/stop</code> - Cancel any active pipeline generation\n"
            "❓ <code>/help</code> - Show this menu"
        )
        send_telegram_message(msg, chat_id)

    elif cmd == "/status" or cmd == "/history":
        send_telegram_message(get_latest_status(), chat_id)

    elif cmd == "/run":
        count = 48
        if len(cmd_parts) > 1:
            try:
                count = int(cmd_parts[1])
            except ValueError:
                count = 48
        success, resp = run_scheduler_async(count=count)
        send_telegram_message(resp, chat_id)

    elif cmd == "/stop":
        global CURRENT_PROCESS
        if CURRENT_PROCESS and CURRENT_PROCESS.poll() is None:
            CURRENT_PROCESS.terminate()
            CURRENT_PROCESS = None
            send_telegram_message("🛑 Pipeline process terminated.", chat_id)
        else:
            send_telegram_message("ℹ️ No active pipeline process is running.", chat_id)
    else:
        send_telegram_message("Unknown command. Type /help to see available commands.", chat_id)

def poll_updates():
    if not BOT_TOKEN:
        print("\n[TelegramController] ⚠️ SETUP REQUIRED:")
        print("  1. Open Telegram on your phone and search for '@BotFather'")
        print("  2. Send '/newbot', give it a name (e.g., 'CuriousByteBot')")
        print("  3. Copy the API Token provided by BotFather.")
        print("  4. Add TELEGRAM_BOT_TOKEN=your_token_here into 'config/.env'")
        print("  5. Message your bot from your phone and run this script again.\n")
        return

    print(f"[TelegramController] Connected to Telegram Bot. Listening for mobile commands...")
    last_update_id = 0

    while True:
        try:
            url = f"{API_BASE}/getUpdates?offset={last_update_id + 1}&timeout=25"
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                for update in data.get("result", []):
                    last_update_id = update["update_id"]
                    message = update.get("message", {})
                    chat_id = str(message.get("chat", {}).get("id", ""))
                    text = message.get("text", "")

                    if text:
                        print(f"  [Mobile Command from {chat_id}]: {text}")
                        # If ALLOWED_CHAT_ID is not configured, lock it to the first user who messages
                        global ALLOWED_CHAT_ID
                        if not ALLOWED_CHAT_ID:
                            ALLOWED_CHAT_ID = chat_id
                            print(f"  ✓ Locked bot notifications to Chat ID: {chat_id}")
                        handle_command(text, chat_id)
            time.sleep(1)
        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    poll_updates()

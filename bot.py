import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

# =====================================================================
# Configuration
# =====================================================================
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TEAM_ID = os.getenv("TEAM_ID", "attack-at-the-knightmares")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not LICHESS_TOKEN:
    raise ValueError("LICHESS_TOKEN is missing. Add it to .env")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Add it to .env")
if not TEAM_ID:
    raise ValueError("TEAM_ID is missing. Add it to .env")

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json",
}

GEMINI_HEADERS = {
    "x-goog-api-key": GEMINI_API_KEY,
    "Content-Type": "application/json",
}

SYSTEM_INSTRUCTION = (
    "You are the AI announcer for the Lichess team "
    "'Attack at the knightmares'. Write one very short, exciting weekly "
    "welcome greeting or match alert. Keep it under two sentences."
)
FALLBACK_ANNOUNCEMENT = "Join our weekly matches! Let's conquer the board! 🐴⚔️"


def get_ai_announcement():
    """Generate an announcement with the Gemini Developer API."""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_INSTRUCTION}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 100},
    }

    try:
        response = requests.post(
            url, json=payload, headers=GEMINI_HEADERS, timeout=20
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return text or FALLBACK_ANNOUNCEMENT
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"[!] Gemini error: {exc}")
        if "404" in str(exc):
            print(f"[!] Check GEMINI_MODEL={GEMINI_MODEL!r} and your API key.")
        print("[*] Using fallback announcement...")
        return FALLBACK_ANNOUNCEMENT


def send_team_announcement(text):
    """Post an announcement to the team as a team leader."""
    url = f"https://lichess.org/api/team/{TEAM_ID}/announce"

    try:
        response = requests.post(
            url,
            headers=LICHESS_HEADERS,
            data={"text": text},
            timeout=20,
        )
        if response.status_code in (200, 201, 204):
            print("[SUCCESS] Announcement posted to the team!")
            return True

        print(f"[!] Lichess announcement rejected: HTTP {response.status_code}")
        print(f"    Response: {response.text[:500]}")
        if response.status_code in (401, 403):
            print("[!] Ensure the token belongs to a team leader and has team:write scope.")
        return False
    except requests.RequestException as exc:
        print(f"[!] Failed to post team announcement: {exc}")
        return False


def check_lichess_account():
    """Verify that the Lichess token is valid and return the username."""
    response = requests.get(
        "https://lichess.org/api/account",
        headers=LICHESS_HEADERS,
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("username", "unknown")


def run_bot_monitor():
    print("[*] Launching Lichess Team Management Automation Engine...")

    try:
        username = check_lichess_account()
        print(f"[✓] Connected as: {username}")
    except (requests.RequestException, ValueError) as exc:
        print(f"[!] Lichess connection failed: {exc}")
        print("[!] Check LICHESS_TOKEN in .env")
        return

    announcement = get_ai_announcement()
    print(f"[*] Drafting Team Announcement: {announcement!r}")
    send_team_announcement(announcement)

    print("[*] Automation loop running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(30)
            try:
                print(f"[Heartbeat]: Connection verified for {check_lichess_account()}")
            except (requests.RequestException, ValueError) as exc:
                print(f"[!] Heartbeat error: {exc}")
    except KeyboardInterrupt:
        print("\n[*] Bot stopped by user")


if __name__ == "__main__":
    run_bot_monitor()

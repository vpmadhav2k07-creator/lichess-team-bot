import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TEAM_ID = os.getenv("TEAM_ID", "attack-at-the-knightmares")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")

if not LICHESS_TOKEN:
    raise ValueError("LICHESS_TOKEN is missing. Add it to .env")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Add it to .env")

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
    "'Attack at the knightmares'. Write one short, exciting weekly "
    "welcome greeting or match alert. Keep it under two sentences."
)
FALLBACK_ANNOUNCEMENT = "Join our weekly matches! Let's conquer the board! 🐴⚔️"


def find_gemini_model():
    """Return a model available to this API key that supports generateContent."""
    if GEMINI_MODEL:
        return GEMINI_MODEL

    response = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        headers={"x-goog-api-key": GEMINI_API_KEY},
        timeout=20,
    )
    response.raise_for_status()
    models = response.json().get("models", [])

    preferred = ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash")
    for wanted in preferred:
        for model in models:
            name = model.get("name", "")
            methods = model.get("supportedGenerationMethods", [])
            if name == f"models/{wanted}" and "generateContent" in methods:
                return wanted

    for model in models:
        name = model.get("name", "")
        methods = model.get("supportedGenerationMethods", [])
        if name.startswith("models/gemini") and "generateContent" in methods:
            return name.removeprefix("models/")

    raise RuntimeError("This Gemini API key has no model supporting generateContent")


def get_ai_announcement():
    """Generate an announcement using a model available to the API key."""
    try:
        model = find_gemini_model()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": SYSTEM_INSTRUCTION}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 100},
        }
        response = requests.post(
            url, json=payload, headers=GEMINI_HEADERS, timeout=20
        )
        response.raise_for_status()
        parts = response.json()["candidates"][0]["content"]["parts"]
        text = "".join(part.get("text", "") for part in parts).strip()
        print(f"[*] Gemini model: {model}")
        return text or FALLBACK_ANNOUNCEMENT
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError, RuntimeError) as exc:
        print(f"[!] Gemini error: {exc}")
        print("[*] Using fallback announcement...")
        return FALLBACK_ANNOUNCEMENT


def send_team_message(message):
    """Send a private update to every team member."""
    url = f"https://lichess.org/team/{TEAM_ID}/pm-all"
    try:
        response = requests.post(
            url,
            headers=LICHESS_HEADERS,
            data={"message": message},
            timeout=20,
        )
        if response.status_code == 200:
            print("[SUCCESS] Private message sent to all team members!")
            return True

        print(f"[!] Lichess rejected the team message: HTTP {response.status_code}")
        print(f"    Response: {response.text[:500]}")
        if response.status_code in (401, 403):
            print("[!] Create a token with the team:lead scope and use a team leader account.")
        return False
    except requests.RequestException as exc:
        print(f"[!] Lichess request failed: {exc}")
        return False


def check_lichess_account():
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
        print(f"[✓] Connected as: {check_lichess_account()}")
    except (requests.RequestException, ValueError) as exc:
        print(f"[!] Lichess connection failed: {exc}")
        return

    message = get_ai_announcement()
    print(f"[*] Drafting Team Message: {message!r}")
    send_team_message(message)

    print("[*] Automation loop running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(30)
            print(f"[Heartbeat]: Connection verified for {check_lichess_account()}")
    except KeyboardInterrupt:
        print("\n[*] Bot stopped by user")
    except (requests.RequestException, ValueError) as exc:
        print(f"[!] Heartbeat error: {exc}")


if __name__ == "__main__":
    run_bot_monitor()

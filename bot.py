import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

# =====================================================================
# ⚙️ CONFIGURATION
# =====================================================================
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TEAM_ID = os.getenv("TEAM_ID", "attack-at-the-knightmares")

if not LICHESS_TOKEN or not GEMINI_API_KEY:
    raise ValueError("ERROR: LICHESS_TOKEN and GEMINI_API_KEY must be set in .env file")
# =====================================================================

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json"
}

GEMINI_HEADERS = {
    "x-goog-api-key": GEMINI_API_KEY,
    "Content-Type": "application/json"
}

SYSTEM_INSTRUCTION = "You are the AI announcer for the Lichess team 'Attack at the knightmares'. Draft a very short, hyper-hype weekly welcome greeting or match alert for your team. Keep it under 2 sentences. Be enthusiastic and fun!"

def get_ai_announcement():
    """Generates the team broadcast text using Google Gemini API."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_INSTRUCTION}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 100}
    }
    try:
        response = requests.post(url, json=payload, headers=GEMINI_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"[!] Gemini Error: {e}")
        return "Join our weekly matches team! Let's conquer the board! 🐴⚔️"


def broadcast_private_msg_to_team():
    """Sends an announcement to team members via Lichess bulletin board."""
    url = f"https://lichess.org/api/team/{TEAM_ID}/bulletin"
    announcement_text = get_ai_announcement()
    
    print(f"[*] Drafting Team Announcement: '{announcement_text}'")
    
    payload_data = {
        "text": announcement_text
    }
    
    try:
        response = requests.post(url, headers=LICHESS_HEADERS, data=payload_data)
        if response.status_code == 200:
            print(f"[SUCCESS] Announcement posted to team bulletin!")
        else:
            print(f"[!] Team Announcement Rejected: HTTP Status {response.status_code}")
            print(f"    Response: {response.text}")
    except Exception as e:
        print(f"[!] Failed to post team announcement: {e}")

def run_bot_monitor():
    print("[*] Launching Lichess Team Management Automation Engine...")
    
    broadcast_private_msg_to_team()
    
    print("[*] Automation loop running successfully!")
    while True:
        try:
            test_response = requests.get("https://lichess.org/api/account", headers=LICHESS_HEADERS)
            if test_response.status_code == 200:
                print(f"[Heartbeat Ping]: Verified connection for account: {test_response.json().get('username')}")
            else:
                print(f"[!] Lichess validation warning code: {test_response.status_code}")
        except Exception as e:
            print(f"[!] Communication error: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    run_bot_monitor()

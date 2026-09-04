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
        print("[*] Using fallback announcement...")
        return "Join our weekly matches team! Let's conquer the board! 🐴⚔️"


def send_team_message(text):
    """Send message to team using the correct API endpoint."""
    # Try multiple endpoint variations
    endpoints = [
        f"https://lichess.org/api/team/{TEAM_ID}/pm",  # Direct PM endpoint
        f"https://lichess.org/api/team/{TEAM_ID}/bulletin",  # Bulletin board
    ]
    
    payload_data = {"text": text}
    
    for url in endpoints:
        try:
            print(f"[*] Trying endpoint: {url}")
            response = requests.post(url, headers=LICHESS_HEADERS, data=payload_data, timeout=10)
            
            if response.status_code in [200, 204]:
                print(f"[SUCCESS] Message sent via {url}!")
                return True
            else:
                print(f"[!] Endpoint failed with status {response.status_code}")
                
        except Exception as e:
            print(f"[!] Error with {url}: {e}")
    
    return False

def broadcast_private_msg_to_team():
    """Sends an announcement to team members."""
    announcement_text = get_ai_announcement()
    print(f"\n[*] Broadcasting: '{announcement_text}'")
    send_team_message(announcement_text)

def run_bot_monitor():
    print("[*] Launching Lichess Team Management Automation Engine...")
    print(f"[*] Team ID: {TEAM_ID}")
    print(f"[*] Token: {LICHESS_TOKEN[:10]}...")
    
    # Test connection first
    try:
        test_response = requests.get("https://lichess.org/api/account", headers=LICHESS_HEADERS, timeout=10)
        if test_response.status_code == 200:
            username = test_response.json().get('username')
            print(f"[✓] Connected as: {username}")
        else:
            print(f"[!] Connection test failed: {test_response.status_code}")
            print("[!] Check your LICHESS_TOKEN in .env file")
            return
    except Exception as e:
        print(f"[!] Failed to connect to Lichess: {e}")
        return
    
    # Send first announcement
    broadcast_private_msg_to_team()
    
    print("\n[*] Automation loop running successfully!")
    print("[*] Press Ctrl+C to stop\n")
    
    while True:
        try:
            time.sleep(30)
            test_response = requests.get("https://lichess.org/api/account", headers=LICHESS_HEADERS, timeout=10)
            if test_response.status_code == 200:
                username = test_response.json().get('username')
                print(f"[Heartbeat]: Connection verified for {username}")
            else:
                print(f"[!] Heartbeat failed: {test_response.status_code}")
                
        except KeyboardInterrupt:
            print("\n[*] Bot stopped by user")
            break
        except Exception as e:
            print(f"[!] Heartbeat error: {e}")

if __name__ == "__main__":
    run_bot_monitor()

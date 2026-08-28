import os
import json
import time
import requests

# =====================================================================
# ⚙️ CONFIGURATION
# =====================================================================
# If your Windows CMD set environment setups wipe memory, paste your 
# raw text keys directly inside these matching quotation marks!
LICHESS_TOKEN = "lip_3FXNpiIKbAcshciR6XyL"
GEMINI_API_KEY = "AQ.Ab8RN6LZz0DezgnfO3tNKVyv8VTEobJC_lpOPKJzyPgCzNr8cA"
TEAM_ID = "attack-at-the-knightmares"  
# =====================================================================

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json"
}

# Secure authorization structure required to pass your key footprint
GEMINI_HEADERS = {
    "x-goog-api-key": GEMINI_API_KEY,
    "Content-Type": "application/json"
}

SYSTEM_INSTRUCTION = "You are the AI announcer for the Lichess team 'Attack at the knightmares'. Draft a very short, hyper-hype weekly welcome greeting or match alert for your team. Keep it under 2 sentences."

def get_ai_announcement():
    """Generates the team broadcast text using the correct Google sub-domain."""
    # Fixed: Added 'generativelanguage' to the domain parameters to clear the 404 flag
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
    """Uses Team Leader rights to send a private inbox message to ALL members."""
    # Fixed: Updated to the real universal Lichess Team messaging endpoint link
    url = f"https://lichess.org/api/team/{TEAM_ID}/pm"
    announcement_text = get_ai_announcement()
    
    print(f"[*] Drafting Team PM: '{announcement_text}'")
    
    # Form layout payload requires passing BOTH the teamId string and text payload
    payload_data = {
        "teamId": TEAM_ID,
        "text": announcement_text
    }
    
    try:
        response = requests.post(url, headers=LICHESS_HEADERS, data=payload_data)
        if response.status_code == 200:
            print(f"[SUCCESS] Blast message deployed to all team members' inboxes!")
        else:
            print(f"[!] Team Blast Rejected: HTTP Status {response.status_code}")
    except Exception as e:
        print(f"[!] Failed to route team broadcast: {e}")

def run_bot_monitor():
    print("[*] Launching Lichess Team Management Automation Engine...")
    
    # Fire the mass PM blast notification sequence instantly on startup
    broadcast_private_msg_to_team()
    
    print("[NO CAP] Your automation anchor loop is running successfully!")
    while True:
        try:
            test_response = requests.get("https://lichess.org/api/account", headers=LICHESS_HEADERS)
            if test_response.status_code == 200:
                print(f"[Heartbeat Ping]: Verified connection for account: {test_response.json().get('username')}")
            else:
                print(f"[!] Lichess validation warning code: {test_response.status_code}")
        except Exception as e:
            print(f"[!] Communication blip: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    run_bot_monitor()

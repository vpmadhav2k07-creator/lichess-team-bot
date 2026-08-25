import os
import json
import time
import requests

# =====================================================================
# ⚙️ CONFIGURATION
# =====================================================================
LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN", "YOUR_TEAM_LEAD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
# Normalized lowercase ID fixes Lichess's strict 404 URL handler
TEAM_ID = "attack-at-the-knightmares"  
# =====================================================================

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json"
}

SYSTEM_INSTRUCTION = "You are the AI announcer for the Lichess team 'Attack at the knightmares'. Draft a very short, hyper-hype weekly welcome greeting or match alert for your team. Keep it under 2 sentences."

def get_ai_announcement():
    """Uses Google Gemini to generate the team broadcast text."""
    # Added 'generativelanguage' to the domain to fix the Google 404 error
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_INSTRUCTION}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 100}
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        # Corrected structure pathway to safely extract the text array
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"[!] Gemini Error: {e}")
        return "Join our weekly matches team! Let's conquer the board! 🐴⚔️"

def broadcast_private_msg_to_team():
    """Uses Team Leader rights to send a private inbox message to ALL members."""
    url = f"https://lichess.org/api/team/{TEAM_ID}/pm"
    announcement_text = get_ai_announcement()
    
    print(f"[*] Drafting Team PM: '{announcement_text}'")
    try:
        response = requests.post(url, headers=LICHESS_HEADERS, data={"text": announcement_text})
        if response.status_code == 200:
            print(f"[SUCCESS] Blast message deployed to all team members' inboxes!")
        else:
            print(f"[!] Team Blast Rejected: HTTP {response.status_code}")
    except Exception as e:
        print(f"[!] Failed to route team broadcast: {e}")

def keep_bot_online():
    """Maintains an active stream state to lock the bot's status to green (Online)."""
    url = "https://lichess.org/api/stream/event"
    print("[*] Launching Lichess Real-Time Event Stream Pipeline...")
    
    # Run a one-time automatic team announcement blast the moment it pops online
    broadcast_private_msg_to_team()
    
    while True:
        try:
            # stream=True keeps the script connected to Lichess so it never switches off
            response = requests.get(url, headers=LICHESS_HEADERS, stream=True, timeout=None)
            if response.status_code == 200:
                print("[NO CAP] Your Bot is officially ONLINE and anchoring the team page!")
                for line in response.iter_lines():
                    if line:
                        event = json.loads(line.decode('utf-8'))
                        print(f"[Activity Ping]: Logged an active backend event -> {event.get('type')}")
            else:
                print(f"[!] Lichess Stream rejected the token: Code {response.status_code}")
                time.sleep(10)
        except Exception as e:
            print(f"[!] Streaming connection dropped, reconnecting in 5s... | Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    keep_bot_online()

import json
import time
import requests

# Configuration
LICHESS_TOKEN = "YOUR_LICHESS_BOT_TOKEN"  
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
BOT_USERNAME = "Ask-AATK-bot"
TEAM_ID = "attack-at-the-knightmares"

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json"
}

SYSTEM_INSTRUCTION = f"""
You are the official conversational AI assistant for the Lichess team 'Attack at the knightmares'. 
A player just asked something in the team chat. You are replying to them PRIVATELY via inbox PM.
Keep your answers under 3 short sentences. Never give active game move advice.
"""

def send_private_message(username, text):
    url = f"https://lichess.org/api/inbox/{username}"
    data = {"text": text}
    response = requests.post(url, headers=LICHESS_HEADERS, data=data)
    return response.status_code

def get_ai_chat_response(player_name, player_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Player '{player_name}' says in team chat: {player_message}"}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response_data = response.json()
        if "candidates" in response_data and response_data["candidates"]:
            return response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return "Go team Attack at the knightmares! 🐴⚔️"
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Go team Attack at the knightmares! 🐴⚔️"

def monitor_team_chat():
    # Utilizing the streaming API instead of history fetching to prevent 404 blocks
    url = f"https://lichess.org/api/team/{TEAM_ID}/chat"
    print(f"Opening live stream chat pipeline for {TEAM_ID}...")
    
    while True:
        try:
            with requests.get(url, headers=LICHESS_HEADERS, stream=True, timeout=60) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            msg = json.loads(line.decode("utf-8"))
                            sender = msg.get("username", "")
                            text = msg.get("text", "").strip()
                            
                            if sender and sender.lower() != BOT_USERNAME.lower() and text:
                                print(f"-> Stream Event from [{sender}]: {text}")
                                reply_text = get_ai_chat_response(sender, text)
                                status = send_private_message(sender, reply_text)
                                print(f"-> Sent PM to {sender} | Status: {status}")
                else:
                    print(f"Server returned status error code: {response.status_code}")
                    time.sleep(10)
        except Exception as e:
            print(f"Stream dropped ({e}). Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    monitor_team_chat()
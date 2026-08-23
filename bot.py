import os
import json
import time
import requests

LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN", "lip_hWWX4phx2UN37HBL69c4")  
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LZz0DezgnfO3tNKVyv8VTEobJC_lpOPKJzyPgCzNr8cA")         
MY_USERNAME = "RegularStrongOwl".lower()          

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json"
}

SYSTEM_INSTRUCTION = "You are the conversational AI for the Lichess team 'Attack at the knightmares'. Keep your answers brief, polite, and under 3 sentences."

def send_private_message(username, text):
    url = f"https://lichess.org/api/inbox/{username}"
    try:
        response = requests.post(url, headers=LICHESS_HEADERS, data={"text": text})
        return response.status_code
    except Exception as e:
        print(f"[!] Error sending PM: {e}")
        return 500

def get_ai_chat_response(player_name, player_message):
    url = f"https://googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Context: {SYSTEM_INSTRUCTION}\n\nPlayer '{player_name}': {player_message}"}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() 
        ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        return ai_text.strip()
    except Exception as e:
        print(f"[!] Gemini API Error: {e}")
        return "Go team Attack at the knightmares! 🐴⚔️"

def monitor_inbox():
    url = "https://lichess.org"
    print("[*] Monitoring user inbox for new messages...")
    known_conversations = {}
    is_first_run = True

    while True:
        try:
            response = requests.get(url, headers=LICHESS_HEADERS)
            if response.status_code == 200:
                conversations = response.json().get("conversations", [])
                for conv in conversations:
                    opponent = conv.get("opponent", {}).get("username", "")
                    last_message = conv.get("lastMessage", {})
                    sender = last_message.get("sender", "")
                    text = last_message.get("text", "").strip()
                    
                    if not opponent or not text:
                        continue
                    if sender.lower() != MY_USERNAME:
                        unique_msg_id = f"{sender}_{text}"
                        if known_conversations.get(opponent) != unique_msg_id:
                            known_conversations[opponent] = unique_msg_id
                            if is_first_run:
                                continue
                            print(f"[Inbox Notification] New message from {sender}: {text}")
                            reply = get_ai_chat_response(sender, text)
                            status = send_private_message(sender, reply)
                            print(f" -> Replied to {sender} | HTTP Status: {status}")
                if is_first_run:
                    is_first_run = False
                    print("[*] Bot successfully caught up. Listening for new PMs...")
            else:
                print(f"[!] Lichess API error flag: {response.status_code}")
        except Exception as e:
            print(f"[!] Cycle check error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    monitor_inbox()

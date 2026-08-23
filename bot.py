import json
import time
import requests

# =====================================================================
# ⚙️ CONFIGURATION: FILL THESE IN
# =====================================================================
# IMPORTANT: Use a regular user account token here. 
# Make sure you checked 'msg:write' when generating this token!
LICHESS_TOKEN = "lip_hWWX4phx2UN37HBL69c4"  
GEMINI_API_KEY = "AQ.Ab8RN6LZz0DezgnfO3tNKVyv8VTEobJC_lpOPKJzyPgCzNr8cA"         
MY_USERNAME = "RegularStrongOwl".lower()          # Your account name in lowercase
# =====================================================================

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json"
}

SYSTEM_INSTRUCTION = """
You are the official conversational AI assistant for the Lichess team 'Attack at the knightmares'. 
A user just messaged you privately in your inbox.
Keep your answers brief, friendly, polite, and under 3 sentences. 
Never offer to play games. Never give tactical advice or live game evaluations.
"""

def send_private_message(username, text):
    """Sends a private message directly to a user's Lichess inbox."""
    url = f"https://lichess.org/api/inbox{username}"
    data = {"text": text}
    try:
        response = requests.post(url, headers=LICHESS_HEADERS, data=data)
        return response.status_code
    except Exception as e:
        print(f"[!] Error sending private message to {username}: {e}")
        return 500

def get_ai_chat_response(player_name, player_message):
    """Generates an answer using the direct Google Gemini 2.5 Flash API."""
      url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": f"Player '{player_name}' messaged you privately: {player_message}"}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "generationConfig": {
            "temperature": 0.7, 
            "maxOutputTokens": 150
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() 
        
        response_json = response.json()
        ai_text = response_json['candidates']['content']['parts']['text']
        return ai_text.strip()
        
    except Exception as e:
        print(f"[!] Gemini API Error: {e}")
        return "Go team Attack at the knightmares! 🐴⚔️"

def monitor_inbox():
    """Polls the user's private message history logs for incoming interactions."""
    # This endpoint pulls the list of recent active chat conversations in your inbox
    url = "https://lichess.org"
    print("[*] Monitoring user inbox for new messages...")
    
    # Store the last message processed for each user to avoid replying to the same text repeatedly
    known_conversations = {}
    is_first_run = True

    while True:
        try:
            response = requests.get(url, headers=LICHESS_HEADERS)
            
            if response.status_code == 200:
                conversations = response.json().get("conversations", [])
                
                for conv in conversations:
                    # Isolate conversation parameters
                    opponent = conv.get("opponent", {}).get("username", "")
                    last_message = conv.get("lastMessage", {})
                    
                    sender = last_message.get("sender", "")
                    text = last_message.get("text", "").strip()
                    
                    if not opponent or not text:
                        continue
                        
                    # We only care if the last message in the thread came from the other person
                    if sender.lower() != MY_USERNAME:
                        unique_msg_id = f"{sender}_{text}"
                        
                        # If it's a completely unseen message signature
                        if known_conversations.get(opponent) != unique_msg_id:
                            known_conversations[opponent] = unique_msg_id
                            
                            # Skip replying to pre-existing messages on initial bot script boot
                            if is_first_run:
                                continue
                                
                            print(f"[Inbox Notification] New message from {sender}: {text}")
                            
                            # Generate and route the response via Gemini
                            reply = get_ai_chat_response(sender, text)
                            status = send_private_message(sender, reply)
                            print(f" -> Replied to {sender} | HTTP Status: {status}")
                
                # Turn off first run flag after parsing the history log the first time
                if is_first_run:
                    is_first_run = False
                    print("[*] Bot successfully caught up with inbox timeline. Listening for new PMs...")
                    
            else:
                print(f"[!] Lichess API returned error flag: {response.status_code}")
                
        except Exception as e:
            print(f"[!] Cycle check error: {e}")
            
        # Wait 5 seconds before checking the inbox loop again to comply with safe rate limits
        time.sleep(5)

if __name__ == "__main__":
    monitor_inbox()
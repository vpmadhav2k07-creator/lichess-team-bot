import json
import time
import requests

# =====================================================================
# ⚙️ CONFIGURATION: SWAP THESE VALUES WITH YOUR REAL DETAILS
# =====================================================================
# WARNING: Do NOT upgrade this account to a Lichess 'BOT'. Keep it a regular user.
LICHESS_TOKEN = "YOUR_PERSONAL_ACCESS_TOKEN"  # Must have 'web:inbox' and 'team:read' scopes
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"         # From Google AI Studio
MY_USERNAME = "Ask-AATK-bot"                   # Your chatbot account username
TEAM_ID = "attack-at-the-knightmares"          # Leave exactly like this
# =====================================================================

LICHESS_HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/json"
}

SYSTEM_INSTRUCTION = f"""
You are the official conversational AI assistant for the Lichess team 'Attack at the knightmares'. 
A user asked something in the public team chat, and you are replying directly in the chat room.
Keep your answers brief, friendly, and under 3 short sentences. 
Never offer to play games. Never give live move advice. 
"""

def post_to_team_chat(text):
    """Sends a public message back into the team chat room channel."""
    url = f"https://lichess.org/api/team/{TEAM_ID}/chat"
    data = {"text": text}
    try:
        response = requests.post(url, headers=LICHESS_HEADERS, data=data)
        return response.status_code
    except Exception as e:
        print(f"[!] Error posting to team chat: {e}")
        return 500

def get_ai_chat_response(player_name, player_message):
    """Generates an answer using the direct Google Gemini 2.5 Flash API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
   payload = {
        "contents": [
            {
                "parts": [{"text": f"Player '{player_name}' said in team chat: {player_message}"}]
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
        ai_text = response_json['candidates'][0]['content']['parts'][0]['text']
        return ai_text.strip()
        
    except Exception as e:
        print(f"[!] Gemini API Error: {e}")
        return "Go team Attack at the knightmares! 🐴⚔️"

def monitor_team_chat():
    """Polls the team chat endpoint and processes new entries securely."""
    # Lichess endpoint to fetch recent chat log history
    url = f"https://lichess.org{TEAM_ID}/chat"
    print(f"[*] Monitoring chat pipeline for team: {TEAM_ID}...")
    
    last_processed_sig = None
    
    while True:
        try:
            # Pull down the last 5 messages from the chat log
            response = requests.get(url, headers=LICHESS_HEADERS, params={"max": 5})
            
            if response.status_code == 200:
                lines = response.text.strip().split("\n")
                if not lines or lines == ['']:
                    time.sleep(4)
                    continue
                
                # Isolate the most recent line written in the chat
                latest_msg = json.loads(lines[-1])
                sender = latest_msg.get("username", "")
                text = latest_msg.get("text", "").strip()
                
                # Unique signature to know if this message is brand new
                current_sig = f"{sender}_{text}"
                
                # First boot configuration: sync with the timeline without replying retrospectively
                if last_processed_sig is None:
                    last_processed_sig = current_sig
                    print("[*] Synchronized with live timeline. Awaiting fresh inputs...")
                
                # Triggered when a completely new chat signature registers
                elif current_sig != last_processed_sig:
                    last_processed_sig = current_sig
                    
                    # Verify the message wasn't posted by our own bot account
                    if sender and sender.lower() != MY_USERNAME.lower() and text:
                        print(f"[Team Chat] {sender}: {text}")
                        
                        # Generate the AI response
                        reply_text = get_ai_chat_response(sender, text)
                        
                        # Format the reply to tag the player who asked
                        final_reply = f"@{sender} {reply_text}"
                        
                        # Ship it out to the team chat page
                        status = post_to_team_chat(final_reply)
                        print(f" -> Posted reply response | HTTP Status: {status}")
                        
            else:
                print(f"[!] Lichess API returned error flag: {response.status_code}")
                
        except Exception as e:
            print(f"[!] Cycle execution error: {e}")
            
        # Wait 4 seconds before reading the chat again to avoid 429 rate limit bans
        time.sleep(4)

if __name__ == "__main__":
    monitor_team_chat()
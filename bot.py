import json
import requests
from google import genai
from google.genai import types

# Configuration
LICHESS_TOKEN = "lip_CjHxk4uP6uOARDa0Ycny"
GEMINI_API_KEY = "AQ.Ab8RN6LZz0DezgnfO3tNKVyv8VTEobJC_lpOPKJzyPgCzNr8cA"
BOT_USERNAME = "Ask-aatk-bot" # Your bot's exact username
TEAM_URL = "https://lichess.org/team/attack-at-the-knightmares"

# Initialize API clients
LICHESS_HEADERS = {"Authorization": f"Bearer {LICHESS_TOKEN}"}
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Custom instructions focusing heavily on team information and strictly banning move advice
SYSTEM_INSTRUCTION = f"""
You are the official conversational AI assistant for the Lichess team 'Attack at the knightmares'. 
Your primary job is to tell players about the team, welcome them, build team spirit, and answer general chess questions.

TEAM DETAILS:
- Name: Attack at the knightmares
- Goal: To play fun tournaments, practice chess together, and improve as a community.
- Team Link: {TEAM_URL}

CRITICAL RULES:
1. You only talk. Do not offer to play games, and do not tell people how to challenge you.
2. ABSOLUTELY PROHIBITED from giving tactical advice, next-best-move suggestions, or live board evaluations. If asked about a live game, decline politely.
3. Keep all responses very short, helpful, and polite (under 3 sentences).
"""

def send_private_message(username, text):
    """Sends a private message directly to a player's Lichess inbox."""
    url = f"https://lichess.org/api/inbox/{username}"
    data = {"text": text}
    response = requests.post(url, headers=LICHESS_HEADERS, data=data)
    return response.status_code

def get_ai_chat_response(player_name, player_message):
    """Generates an answer via Gemini AI representing the team."""
    prompt = f"Player '{player_name}' messaged you privately: {player_message}"
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-3.7-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I had trouble reading that. Go team Attack at the knightmares! 🐴"

def stream_incoming_messages_only():
    """Streams Lichess events but explicitly filters for text messages only."""
    url = "https://lichess.org/api/ste"
    print("Bot is online. Listening ONLY for private chat messages...")
    
    with requests.get(url, headers=LICHESS_HEADERS, stream=True) as response:
        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode("utf-8"))
                    event_type = event.get("type")
                    
                    # Log and ignore any challenge attempts
                    if event_type == "challenge":
                        challenge_id = event.get("challenge", {}).get("id")
                        print(f"Ignored a game challenge (ID: {challenge_id}) because this bot is chat-only.")
                        continue
                    
                    # Only respond to private inbox text messages
                    if event_type == "message":
                        msg_data = event.get("message", {})
                        sender = msg_data.get("username", "")
                        text = msg_data.get("text", "").strip()
                        
                        # Prevent responding to your own text loops
                        if sender.lower() == BOT_USERNAME.lower() or not text:
                            continue
                            
                        print(f"Private Msg from [{sender}]: {text}")
                        
                        # Generate team-focused response and send it
                        reply_text = get_ai_chat_response(sender, text)
                        send_private_message(sender, reply_text)
                        print(f"Sent reply to [{sender}]: {reply_text}")
                        
                except Exception as e:
                    print(f"Error handling event: {e}")

if __name__ == "__main__":
    stream_incoming_messages_only()
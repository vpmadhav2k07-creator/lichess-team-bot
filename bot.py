import json
import time
import requests

# Configuration
LICHESS_TOKEN = "YOUR_LICHESS_BOT_TOKEN"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
BOT_USERNAME = "knightmaresbot"  # Your bot's exact username
TEAM_URL = "https://lichess.org/team/attack-at-the-knightmares"

LICHESS_HEADERS = {"Authorization": f"Bearer {LICHESS_TOKEN}"}

SYSTEM_INSTRUCTION = f"""
You are the official conversational AI assistant for the Lichess team 'Attack at the knightmares'. 
Your primary job is to tell players about the team, welcome them, build team spirit, and answer general chess questions.

TEAM DETAILS:
- Name: Attack at the knightmares
- Team Link: {TEAM_URL}

CRITICAL RULES:
1. You only talk. Do not offer to play games, and do not tell people how to challenge you.
2. ABSOLUTELY PROHIBITED from giving tactical advice, next-best-move suggestions, or live board evaluations.
3. Keep all responses very short, helpful, and polite (under 3 sentences).
"""


def send_private_message(username, text):
    """Sends a private message directly to a player's Lichess inbox."""
    url = f"https://lichess.org/api/inbox/{username}"
    data = {"text": text}
    response = requests.post(url, headers=LICHESS_HEADERS, data=data)
    return response.status_code


def get_ai_chat_response(player_name, player_message):
    """Generates an answer using a direct HTTP request to Gemini."""
    # We use gemini-2.5-flash as it is the standard stable endpoint
    url = f"https://googleapis.com{GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Player '{player_name}' messaged you privately: {player_message}"
                    }
                ]
            }
        ],
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150},
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response_data = response.json()
        # Extract the text response cleanly from the JSON structure
        reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return reply.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I had trouble reading that. Go team Attack at the knightmares! 🐴"


def stream_incoming_messages_only():
    """Streams Lichess events but explicitly filters for text messages only."""
    url = "https://lichess.org/api/stream/event"
    print("Bot connection opened. Listening ONLY for private chat messages...")

    with requests.get(url, headers=LICHESS_HEADERS, stream=True) as response:
        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode("utf-8"))
                    event_type = event.get("type")

                    if event_type == "challenge":
                        continue

                    if event_type == "message":
                        msg_data = event.get("message", {})
                        sender = msg_data.get("username", "")
                        text = msg_data.get("text", "").strip()

                        if sender.lower() == BOT_USERNAME.lower() or not text:
                            continue

                        print(f"Private Msg from [{sender}]: {text}")

                        reply_text = get_ai_chat_response(sender, text)
                        send_private_message(sender, reply_text)
                        print(f"Sent reply to [{sender}]: {reply_text}")

                except Exception as e:
                    print(f"Error handling event: {e}")


if __name__ == "__main__":
    while True:
        try:
            stream_incoming_messages_only()
        except Exception as crash_error:
            print(f"Bot disconnected or stream closed: {crash_error}")
            print("Attempting to reconnect to Lichess in 10 seconds...")
            time.sleep(10)
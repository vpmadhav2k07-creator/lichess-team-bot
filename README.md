# Lichess Team Bot 🐴♟️

An automated bot that sends AI-generated announcements to your Lichess team using the Gemini API.

## 📋 Prerequisites

- Python 3.8+
- A Lichess account with team leader permissions
- A Google Cloud API key for Gemini

## 🔑 Getting Your Tokens

### 1. Lichess Token

1. Go to https://lichess.org/account/oauth/token
2. Click **"New personal access token"**
3. Give it a name (e.g., "Team Bot")
4. Under **Scopes**, select:
   - ✅ `team:write` (to post announcements)
   - ✅ `team:read` (to read team info)
5. Click **"Create**
6. **Copy the token** (it starts with `lip_`)
7. Save it somewhere safe - you won't see it again!

### 2. Google Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click **"Create API Key"**
3. Select your project (or create a new one)
4. Copy the API key
5. Save it somewhere safe

## ⚙️ Setup Instructions

### Step 1: Install Dependencies

Open Command Prompt in your project folder and run:

```cmd
pip install -r requirements.txt
```

### Step 2: Create `.env` File

1. In the same folder as `bot.py`, create a file named `.env` (no extension)
2. Copy this template and fill in YOUR tokens:

```env
LICHESS_TOKEN=lip_your_token_here
GEMINI_API_KEY=your_gemini_key_here
TEAM_ID=attack-at-the-knightmares
```

**Example:**
```env
LICHESS_TOKEN=lip_3FXNpiIKbAcshciR6XyL
GEMINI_API_KEY=AQ.Ab8RN6I4SXTBuPjKw8qO0ZQCI-ff22pTmgpPJmLVYZ2Dppzwog
TEAM_ID=attack-at-the-knightmares
```

> ⚠️ **Never commit `.env` to git!** It's already in `.gitignore`

### Step 3: Run the Bot

```cmd
python bot.py
```

You should see:
```
[*] Launching Lichess Team Management Automation Engine...
[*] Drafting Team Announcement: '...'
[SUCCESS] Announcement posted to team bulletin!
[*] Automation loop running successfully!
[Heartbeat Ping]: Verified connection for account: your_username
```

## 🛑 Stopping the Bot

Press `Ctrl + C` in Command Prompt

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'dotenv'`
Run: `pip install python-dotenv`

### `ModuleNotFoundError: No module named 'requests'`
Run: `pip install requests`

### Or install all at once:
```cmd
pip install -r requirements.txt
```

### Invalid token error
- Check your `.env` file is in the correct folder
- Make sure your Lichess token starts with `lip_`
- Regenerate your token if needed

### API key not working
- Verify your Gemini API key is correct
- Check you have API access enabled in Google Cloud Console
- Make sure the key has Generative Language API enabled

## 📝 Files Explained

- **bot.py** - Main bot code
- **requirements.txt** - Python dependencies
- **.env** - Your credentials (create this, don't commit!)
- **.env.example** - Template for `.env`
- **.gitignore** - Prevents secrets from being uploaded

## 🔒 Security

✅ API keys are loaded from `.env` - not hardcoded
✅ `.env` is in `.gitignore` - won't be committed
✅ Safe to push code to GitHub

## 📚 Learn More

- [Lichess API Docs](https://lichess.org/api)
- [Google Gemini API](https://ai.google.dev/)
- [python-dotenv Documentation](https://python-dotenv.readthedocs.io/)

---

**Happy team announcements!** 🎉

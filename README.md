# Auto Response Bot (@auto_response1bot)

A Telegram bot that automatically replies to messages with pre-defined responses.

## Features
- 🤖 Auto-reply to messages with keyword-based responses
- 🖼️ Image processing (stub for conversion/generation)
- 🔗 URL shortening (stub for link shortening)
- 👋 Welcome message for new users

## Deployment on Railway

1. Fork this repository to your GitHub account
2. Create a new project on Railway
3. Connect your GitHub repository
4. Add environment variable `TELEGRAM_BOT_TOKEN` with your bot token
5. Deploy!

## Setting Up Webhook

After deployment, visit:
`https://your-railway-url.railway.app/setwebhook?url=https://your-railway-url.railway.app`

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variable: `export TELEGRAM_BOT_TOKEN=your_token`
4. Run the app: `python app.py`
5. Set webhook to local ngrok URL

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your bot's API token from BotFather
- `PORT`: Port for the server (Railway sets this automatically)
- `RAILWAY_STATIC_URL`: Your Railway URL (set automatically)

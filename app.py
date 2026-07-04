import os
import logging
from flask import Flask, request, jsonify
import requests
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Fallback for local testing

# Telegram API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Auto-reply configurations
AUTO_REPLY_CONFIG = {
    # Keywords that trigger specific replies
    "keywords": {
        "hello": "👋 Hello! Welcome to Auto Response Bot. How can I help you today?",
        "hi": "👋 Hi there! I'm here to assist you. What do you need?",
        "help": "🆘 I can help you with:\n- Answering questions\n- Providing information\n- Just having a chat\n\nWhat would you like to know?",
        "how are you": "🤖 I'm doing great! Thanks for asking. How about you?",
        "what is your name": "🤖 I'm Auto Response Bot! You can call me AutoBot for short.",
        "who are you": "🤖 I'm a friendly auto-reply bot created to assist you. My username is @auto_response1bot.",
        "bye": "👋 Goodbye! Have a great day! Feel free to come back anytime.",
        "goodbye": "👋 See you later! Take care!",
        "thanks": "😊 You're welcome! Always happy to help.",
        "thank you": "😊 My pleasure! Is there anything else I can do for you?",
        "yes": "✅ Great! What would you like me to help you with?",
        "no": "❌ No problem! If you need anything else, just let me know."
    },
    "default_reply": "🤔 I'm not sure how to respond to that. I'm still learning! Try saying 'hello' or 'help' to get started.",
    "welcome_message": "🎉 Welcome to Auto Response Bot!\n\nI'm here to help you with your questions. Just send me a message and I'll do my best to assist you.\n\nTry saying:\n- 'hello' to start a conversation\n- 'help' to see what I can do\n- 'bye' to end the conversation"
}

def send_message(chat_id, text):
    """Send a message to a Telegram user"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Message sent to {chat_id}: {text[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def process_message(text):
    """Process incoming message and generate auto-reply"""
    text_lower = text.lower().strip()
    
    # Check for URL shortener request
    if "shorten" in text_lower and "http" in text_lower:
        # Extract URL from message
        url_match = re.search(r'(https?://[^\s]+)', text)
        if url_match:
            url_to_shorten = url_match.group(1)
            # Simulate URL shortening (in real implementation, use a URL shortener API)
            short_url = f"https://short.link/{hash(url_to_shorten) % 1000000:06d}"
            return f"🔗 Here's your shortened URL: <b>{short_url}</b>\n\nOriginal: {url_to_shorten}"
        else:
            return "❌ Please provide a valid URL to shorten. Example: 'shorten https://example.com'"
    
    # Check for image conversion request
    if "convert" in text_lower and ("image" in text_lower or "jpg" in text_lower or "png" in text_lower):
        return "🖼️ To convert an image, please send me the image file directly. I'll convert it to your preferred format.\n\nSupported formats: JPG, PNG, GIF, BMP, WebP"
    
    # Check for image generation request
    if "generate" in text_lower and ("image" in text_lower or "picture" in text_lower or "ai" in text_lower):
        # Simulate image generation (in real implementation, use an AI image generator API)
        return "🎨 I'm generating your image...\n\nAI image generation is a complex process. In production, you could integrate with DALL-E, Stable Diffusion, or other AI image generators.\n\nYour prompt: " + text
    
    # Check keywords
    for keyword, reply in AUTO_REPLY_CONFIG["keywords"].items():
        if keyword in text_lower:
            return reply
    
    # Return default reply if no keyword matches
    return AUTO_REPLY_CONFIG["default_reply"]

@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return jsonify({"status": "active", "message": "Auto Response Bot is running!"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram messages"""
    try:
        # Get the incoming update
        update = request.get_json()
        logger.info(f"Received update: {json.dumps(update)[:200]}...")
        
        # Check if it's a message
        if 'message' not in update:
            return jsonify({"status": "ok"}), 200
        
        message = update['message']
        chat_id = message.get('chat', {}).get('id')
        
        # If it's a new chat member (user joined), send welcome message
        if 'new_chat_members' in message:
            welcome_text = AUTO_REPLY_CONFIG["welcome_message"]
            send_message(chat_id, welcome_text)
            return jsonify({"status": "ok"}), 200
        
        # If it's a text message
        if 'text' in message:
            text = message['text']
            logger.info(f"Received message from {chat_id}: {text}")
            
            # Generate auto-reply
            reply_text = process_message(text)
            send_message(chat_id, reply_text)
            
        # If it's a photo or document (image file)
        elif 'photo' in message or ('document' in message and message['document'].get('mime_type', '').startswith('image/')):
            reply_text = "🖼️ I received your image! To convert it, reply with:\n\n• 'convert to PNG'\n• 'convert to JPG'\n• 'convert to WEBP'\n\nI'll process your image and send back the converted version."
            send_message(chat_id, reply_text)
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    """Manually set the webhook URL"""
    try:
        # Get Railway URL from environment or request
        railway_url = request.args.get('url')
        if not railway_url:
            # Try to get from environment
            railway_url = os.environ.get('RAILWAY_STATIC_URL')
            if not railway_url:
                return jsonify({"error": "No URL provided. Please provide ?url=YOUR_RAILWAY_URL"}), 400
        
        # Ensure the URL ends with /webhook
        if not railway_url.endswith('/webhook'):
            if railway_url.endswith('/'):
                railway_url += 'webhook'
            else:
                railway_url += '/webhook'
        
        webhook_url = f"{TELEGRAM_API_URL}/setWebhook?url={railway_url}"
        response = requests.get(webhook_url)
        response.raise_for_status()
        
        return jsonify({
            "status": "success",
            "message": f"Webhook set to {railway_url}",
            "response": response.json()
        }), 200
    
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/getwebhookinfo', methods=['GET'])
def get_webhook_info():
    """Get current webhook information"""
    try:
        url = f"{TELEGRAM_API_URL}/getWebhookInfo"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

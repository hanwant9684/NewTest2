"""
Wrapper to run Telegram bot with Flask web server for Render deployment
This satisfies Render's port binding requirement while keeping the bot running
"""
import os
import sys
from flask import Flask, jsonify, render_template, request
from ad_monetization import ad_monetization

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'message': 'Telegram Bot is running!',
        'bot': 'Restricted Content Downloader'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/watch-ad')
def watch_ad():
    session_id = request.args.get('session', '')
    verification_url = request.args.get('verification_url', '')
    ad1_url = request.args.get('ad1_url', '')
    ad2_url = request.args.get('ad2_url', '')
    ad3_url = request.args.get('ad3_url', '')
    
    response = app.make_response(render_template('ad_verify.html', 
                         session=session_id,
                         verification_url=verification_url,
                         ad1_url=ad1_url, 
                         ad2_url=ad2_url, 
                         ad3_url=ad3_url))
    
    # Add security headers to prevent iframes from breaking out
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none';"
    response.headers['Permissions-Policy'] = 'fullscreen=(), payment=(), geolocation=(), microphone=(), camera=()'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    
    return response

@app.route('/api/verify-session', methods=['POST'])
def verify_session():
    """API endpoint to verify ad completion and get verification code"""
    data = request.get_json()
    session_id = data.get('session', '')
    
    success, code, message = ad_monetization.verify_ad_completion(session_id)
    
    return jsonify({
        'success': success,
        'code': code,
        'message': message
    })

def run_bot():
    """Run the Telegram bot in a background thread with long polling"""
    import asyncio
    
    # Set uvloop policy for better performance (before creating loop)
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass
    
    # Create and set event loop BEFORE importing main
    # This ensures Pyrogram Client has an event loop during initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Now import main - Pyrogram will see the event loop
    import main
    
    async def start_bot():
        """Start bot without signal handlers (thread-safe)"""
        try:
            main.LOGGER(__name__).info("Starting Telegram bot from server.py (long polling)")
            await main.bot.start()
            main.LOGGER(__name__).info("Bot started successfully, waiting for updates...")
            # Keep the bot running without signal handlers (thread-safe alternative to idle())
            await asyncio.Event().wait()
        finally:
            await main.bot.stop()
            main.LOGGER(__name__).info("Bot stopped")
    
    # Run the async coroutine on this thread's event loop
    loop.run_until_complete(start_bot())

# Start bot process when app initializes (for Gunicorn workers)
import threading
bot_started = False
bot_lock = threading.Lock()

def start_bot_once():
    """Start bot only once across all workers"""
    global bot_started
    with bot_lock:
        if not bot_started:
            print(f"Starting Telegram bot in background thread...")
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
            bot_started = True

# Start bot when module loads (for Gunicorn)
start_bot_once()

if __name__ == '__main__':
    # This runs only for development (Replit, local testing)
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask development server on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

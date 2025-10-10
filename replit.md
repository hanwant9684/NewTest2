# Restricted Content Downloader Telegram Bot

## Overview
Advanced Telegram bot that downloads restricted content (photos, videos, audio files, documents) from Telegram private chats or channels. Features user authentication, database management, admin controls, and Monetag ad monetization.

## Project Setup (Completed)
- **Language**: Python 3.11
- **Database**: MongoDB for user management and ad sessions
- **Dependencies**: Pyrofork, TgCrypto, Pyleaves, python-dotenv, psutil, pillow, uvloop, flask, pymongo
- **Bot Type**: Backend Telegram Bot (Console Application)
- **Deployment**: VM deployment (stateful, always running)
- **Performance**: Optimized for fast downloads/uploads with uvloop and parallel transfers

## Current State (2025-10-10)
✅ Python 3.11 installed  
✅ All dependencies installed (including uvloop for speed)
✅ Database system using MongoDB
✅ **Monetag ad monetization** - Watch ads for free premium access
✅ Phone authentication system added
✅ Access control & user management
✅ Admin commands implemented
✅ Premium/Free tier system (ads or $1/month paid)
✅ Workflow configured to run `python server.py` (Flask + Bot)
✅ Deployment configuration set for VM target  
✅ .gitignore properly configured
✅ **Performance optimizations implemented:**
  - uvloop for 2-4x faster async operations
  - Parallel file transfers (max_concurrent_transmissions=8)
  - Optimized worker threads (workers=8)
  - TgCrypto for faster cryptographic operations
✅ **Race condition fixed** - Atomic session verification prevents duplicate codes
✅ **Download Queue System** - 20 concurrent downloads + 100 waiting queue with priority for premium users

## Configuration Required

### 1. Required API Credentials
Set up via Replit Secrets or `config.env`:
- `API_ID`: Your Telegram API ID from [my.telegram.org](https://my.telegram.org)
- `API_HASH`: Your Telegram API Hash from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN`: Bot token from [@BotFather](https://t.me/BotFather)
- `OWNER_ID`: Your Telegram user ID (auto-added as admin on first start)
- `MONGODB_URI`: MongoDB connection string for database
- `SESSION_STRING`: (Optional) Fallback session string
- `APP_URL`: (Optional) Custom domain URL for ad verification

### 2. Monetag Ad Configuration (Optional)
For free premium access via ads - **supports up to 10 ad slots**:
- `AD_ID_1`: Monetag zone ID for ad slot 1
- `AD_ID_2`: Monetag zone ID for ad slot 2
- `AD_ID_3`: Monetag zone ID for ad slot 3
- `AD_ID_4`: Monetag zone ID for ad slot 4
- `AD_ID_5`: Monetag zone ID for ad slot 5
- `AD_ID_6`: Monetag zone ID for ad slot 6
- `AD_ID_7`: Monetag zone ID for ad slot 7
- `AD_ID_8`: Monetag zone ID for ad slot 8
- `AD_ID_9`: Monetag zone ID for ad slot 9
- `AD_ID_10`: Monetag zone ID for ad slot 10

**Notes**: 
- Configure only the ad slots you want to use (1-10 ads supported)
- Each AD_ID can contain multiple zone IDs (comma-separated) for random rotation
- Users will watch all configured ads in sequence to get premium access

### 3. Payment Configuration (For $1/month subscription)
- `ADMIN_USERNAME`: Admin Telegram username for payment contact
- `PAYPAL_URL`: PayPal payment link
- `UPI_ID`: UPI ID for payments (India)

### 4. First Time Setup
- Bot automatically connects to MongoDB on first run
- Owner (set via OWNER_ID) is automatically added as admin
- Users must login with their phone numbers to use the bot

## Platform Deployment

The bot automatically detects the domain based on your hosting platform!

### Deployment Files
- **railway.json** - Railway.app deployment configuration (included)
- **server.py** - Flask wrapper for web server deployment
- **Procfile** - Not needed (railway.json handles this)

### Supported Platforms:

#### 🚂 Railway.app (Recommended)
1. Push your code to GitHub
2. Import repository to Railway
3. Railway automatically detects `railway.json`
4. Add environment variables in Railway dashboard
5. Deploy! Domain is auto-detected via `RAILWAY_PUBLIC_DOMAIN`

**Environment Variables Needed:**
- API_ID, API_HASH, BOT_TOKEN, OWNER_ID, MONGODB_URI
- Optional: AD_ID_1 through AD_ID_10 (up to 10 ad slots), ADMIN_USERNAME, PAYPAL_URL, UPI_ID

#### 🖥️ IONOS VPS
1. SSH into your VPS server
2. Clone the repository
3. Install Python 3.11 and dependencies: `pip install -r requirements.txt`
4. Create `config.env` file with your credentials
5. Set `APP_URL=https://yourdomain.com` in config.env
6. Run: `python server.py` or use systemd/supervisor for auto-restart

#### ☁️ Other Platforms
- **Render**: Uses `RENDER_EXTERNAL_URL` (auto-detected)
- **Heroku**: Uses `HEROKU_APP_NAME` (auto-detected)
- **Replit**: Uses `REPLIT_DEV_DOMAIN` (auto-detected)

### Manual Domain Override (Optional):
If auto-detection fails, set manually:
```bash
APP_URL=https://your-custom-domain.com
```

## Key Features

### 🚀 Download Queue System
- **20 Concurrent Downloads**: Process up to 20 downloads simultaneously
- **100 Waiting Queue**: Up to 100 downloads can wait in queue
- **Priority Queue**: Premium ($1) users get priority over free users
- **Queue Status**: `/queue` command to check your position
- **Global Status**: `/qstatus` (admin) to view system-wide queue status
- **Smart Management**: Automatic queue processing and user notifications

### 🔐 User Authentication System
- **Phone Number Login**: Users login with their own phone numbers
- **OTP Verification**: Secure OTP-based authentication
- **2FA Support**: Full support for two-factor authentication
- **Personal Sessions**: Each user gets their own Telegram session
- **No Shared Credentials**: Eliminates SESSION_STRING conflicts

### 👥 User Management & Access Control
- **Free Users**: 5 downloads per day
- **Premium Users**: Unlimited downloads + batch features
- **Admin Users**: Full access + management commands
- **Ban System**: Ban/unban users from the bot
- **User Tracking**: Track downloads, activity, and subscriptions

### 📊 Database System
- **MongoDB Database**: Stores user data, sessions, and statistics
- **User Profiles**: Track username, join date, activity
- **Daily Limits**: Automatic reset of daily download quotas
- **Subscription Management**: Premium expiry tracking
- **Broadcast History**: Log all broadcasts sent
- **Ad Sessions**: Cross-process session sharing with TTL expiration

### 🎯 Download Features
- Download media (photos, videos, audio, documents)
- Support for single media posts and media groups
- Real-time progress bars during downloads
- Copy text messages or captions from Telegram posts
- Batch download (Premium only)
- Personal user sessions for restricted content

## User Commands

### Basic Commands
- `/start` - Welcome message and setup instructions
- `/help` - Detailed help and examples
- `/myinfo` - View account info, limits, and subscription
- `/stats` - View bot system statistics

### Authentication Commands
- `/login +1234567890` - Start login with phone number
- `/verify 1 2 3 4 5` - Enter OTP code (with spaces)
- `/password <2FA_password>` - Enter 2FA password if enabled
- `/logout` - Logout from account
- `/cancel` - Cancel pending authentication

### Premium Commands
- `/getpremium` - Watch Monetag ads for 30 minutes of FREE premium
- `/verifypremium <code>` - Verify ad completion code
- `/upgrade` - View all premium options ($1/month or watch ads)

### Queue Commands
- `/queue` - Check your download queue position
- `/canceldownload` - Cancel your active download or remove from queue
- `/qstatus` - View global queue status (admin only)

### Download Commands
- `/dl <post_URL>` - Download media from Telegram post
- `/bdl <start_link> <end_link>` - Batch download (Premium only)
- Just paste a link - Auto-download without command

## Admin Commands

### User Management
- `/addadmin <user_id>` - Add new administrator
- `/removeadmin <user_id>` - Remove admin privileges
- `/setpremium <user_id> [days]` - Grant premium (default 30 days)
- `/removepremium <user_id>` - Remove premium subscription
- `/ban <user_id>` - Ban user from bot
- `/unban <user_id>` - Unban user
- `/userinfo` - Get user information

### Bot Management
- `/adminstats` - Detailed bot statistics
- `/broadcast <message>` - Send message to all users
- `/logs` - Download bot logs (admin only)
- `/killall` - Cancel all pending downloads

## Premium Access Options

### Option 1: Watch Ads (FREE)
- Use `/getpremium` command
- Watch 3 Monetag video ads
- Get 30 minutes of premium access
- Repeat anytime for more premium time

### Option 2: Monthly Subscription ($1 USD)
- Pay $1 via PayPal or UPI
- Contact admin with payment proof
- Get 30 days of premium access
- Unlimited downloads + batch features

## Usage Limits
- **Free Users**: 5 downloads per day
- **Premium Users**: Unlimited downloads
- **Admin Users**: Unlimited downloads + management access

## Recent Changes (2025-10-10)

### Latest Updates
- ✅ **10 Ad Slot Support** - Configure up to 10 Monetag ads (AD_ID_1 through AD_ID_10)
- ✅ **Dynamic Ad Rendering** - Template automatically adjusts based on configured ads
- ✅ **Fixed Ad Display Issues** - Added proper iframe sandbox permissions (allow-forms, allow-top-navigation)
- ✅ **Railway Deployment Optimization** - Using gunicorn for 50% faster performance

### Previous Updates
- ✅ **Removed Adsterra and Adsgram** - Now using Monetag only
- ✅ **Simplified configuration** - Fewer environment variables needed
- ✅ **Removed /watchad command** - Use /getpremium for ads
- ✅ **Added railway.json** - Railway.app deployment support
- ✅ **Updated documentation** - Clear Monetag-only setup guide with Railway & IONOS VPS instructions

### Previous Changes (2025-10-08 to 2025-10-09)
- ✅ **Platform-agnostic deployment** - Works on Railway, Render, Heroku, VPS
- ✅ **Download queue system** - 20 concurrent + 100 waiting queue
- ✅ **Ad monetization session fix** - Database-backed session storage
- ✅ **Race condition prevention** - Atomic verification operations

## Architecture

### Core Files
- **main.py** - Bot initialization, command handlers, and routing
- **server.py** - Flask web server wrapper for deployment
- **config.py** - Environment variable handling and configuration
- **database.py** - MongoDB database manager for user data
- **phone_auth.py** - Phone number authentication handler
- **access_control.py** - Decorators for permissions and limits
- **admin_commands.py** - Admin command implementations
- **ad_monetization.py** - Monetag ad-based premium system with session management
- **queue_manager.py** - Priority-based download queue system (20 active + 100 waiting)

### Helper Modules
- **helpers/files.py** - File operations and size handling
- **helpers/msg.py** - Message parsing and link processing  
- **helpers/utils.py** - Media processing and upload utilities
- **logger.py** - Structured logging configuration

### Database Schema
- **users** - User profiles, sessions, subscriptions
- **admins** - Administrator privileges
- **daily_usage** - Download limits tracking
- **broadcasts** - Broadcast history
- **ad_sessions** - Temporary ad verification sessions
- **verification_codes** - Ad completion verification codes

## Security Features
- Encrypted session storage in database
- Individual user sessions (no shared credentials)
- Admin-only commands with decorators
- Ban system to prevent abuse
- Daily rate limiting for free users
- Secure OTP and 2FA authentication
- Atomic session verification (prevents race conditions)

## Monetag Ad Setup Guide

### Step 1: Get Monetag Account
1. Sign up at [Monetag](https://monetag.com)
2. Create ad zones in your dashboard
3. Copy your zone IDs

### Step 2: Configure Environment Variables
Configure 1 to 10 ad slots as needed:
```bash
AD_ID_1=your_zone_id_1
AD_ID_2=your_zone_id_2
AD_ID_3=your_zone_id_3
# Add more if needed (up to AD_ID_10)
AD_ID_4=your_zone_id_4
AD_ID_5=your_zone_id_5
```

**Tips:**
- Use 2-3 ads for balanced user experience
- Each ad = 30 seconds watch time
- More ads = more revenue but may reduce completion rate

### Step 3: Test the System
1. Deploy your bot
2. Use `/getpremium` command
3. Watch all configured ads (30 seconds each)
4. Complete AdEx verification if shown
5. Get your verification code
6. Enjoy 30 minutes of premium!

### AdEx Verification Note
Some Monetag ads include AdEx "Verify you are human" checks. Due to security restrictions, the timer cannot wait for verification completion - users must complete it quickly within the 30-second window.

### Ad Revenue
- Users watch ads to get free premium
- You earn revenue from Monetag based on views
- Typical CPM: $1-$10 depending on geography
- Instant payouts available

## Support
For issues or questions, contact the admin specified in `ADMIN_USERNAME` environment variable.

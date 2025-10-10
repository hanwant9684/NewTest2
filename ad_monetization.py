import os
import secrets
import hashlib
import random
from datetime import datetime, timedelta
from logger import LOGGER
from database import db

PREMIUM_DURATION_MINUTES = 30
AD_WATCH_DURATION_SECONDS = 30
SESSION_VALIDITY_MINUTES = 5

class AdMonetization:
    def __init__(self):
        from config import PyroConf
        
        # Support for up to 10 ad slots with multiple zone IDs for rotation
        self.ad_zone_ids = {}
        
        for i in range(1, 11):
            ad_id_attr = f"AD_ID_{i}"
            ad_ids = getattr(PyroConf, ad_id_attr, "")
            self.ad_zone_ids[i] = [zone_id.strip() for zone_id in ad_ids.split(',') if zone_id.strip()] if ad_ids else []
        
        # Count configured ads
        configured_ads = sum(1 for zones in self.ad_zone_ids.values() if zones)
        LOGGER(__name__).info(f"Monetag ad network configured with {configured_ads} ad slot(s)")
    
    def _get_random_zone_id(self, ad_slot: int = 1) -> str:
        """Get a random zone ID from the configured zones for ad variety
        ad_slot: 1-10 for different ad slots
        """
        if ad_slot in self.ad_zone_ids and self.ad_zone_ids[ad_slot]:
            return random.choice(self.ad_zone_ids[ad_slot])
        return ""
    
    def create_ad_session(self, user_id: int) -> str:
        """Create a temporary session for ad watching"""
        session_id = secrets.token_hex(16)
        db.create_ad_session(session_id, user_id)
        
        LOGGER(__name__).info(f"Created ad session {session_id} for user {user_id}")
        return session_id
    
    def verify_ad_completion(self, session_id: str) -> tuple[bool, str, str]:
        """Verify that user watched the ad and generate verification code (atomic operation)"""
        session_data = db.get_ad_session(session_id)
        
        if not session_data:
            return False, "", "❌ Invalid or expired session. Please start over with /getpremium"
        
        # Check if session expired (5 minutes max for the whole flow)
        elapsed_time = datetime.now() - session_data['created_at']
        if elapsed_time > timedelta(minutes=SESSION_VALIDITY_MINUTES):
            db.delete_ad_session(session_id)
            return False, "", "⏰ Session expired. Please start over with /getpremium"
        
        # Check if enough time has passed (must watch ad for at least 30 seconds)
        elapsed_seconds = elapsed_time.total_seconds()
        if elapsed_seconds < AD_WATCH_DURATION_SECONDS:
            remaining = AD_WATCH_DURATION_SECONDS - int(elapsed_seconds)
            return False, "", f"⏰ Please watch the ad for at least {AD_WATCH_DURATION_SECONDS} seconds. Time remaining: {remaining} seconds"
        
        # Atomically mark session as used (prevents race condition)
        success = db.mark_ad_session_used(session_id)
        if not success:
            return False, "", "❌ This session has already been used. Please use /getpremium to get a new link."
        
        # Generate verification code
        verification_code = self._generate_verification_code(session_data['user_id'])
        
        # Delete session after successful verification
        db.delete_ad_session(session_id)
        
        LOGGER(__name__).info(f"User {session_data['user_id']} completed ad session {session_id}, generated code {verification_code}")
        return True, verification_code, "✅ Ad completed! Here's your verification code"
    
    def _generate_verification_code(self, user_id: int) -> str:
        """Internal method to generate verification code after ad is watched"""
        code = secrets.token_hex(4).upper()
        db.create_verification_code(code, user_id)
        
        LOGGER(__name__).info(f"Generated verification code {code} for user {user_id}")
        return code
    
    def verify_code(self, code: str, user_id: int) -> tuple[bool, str]:
        code = code.upper().strip()
        
        verification_data = db.get_verification_code(code)
        
        if not verification_data:
            return False, "❌ **Invalid verification code.**\n\nPlease make sure you entered the code correctly or get a new one with `/getpremium`"
        
        if verification_data['user_id'] != user_id:
            return False, "❌ **This verification code belongs to another user.**"
        
        created_at = verification_data['created_at']
        if datetime.now() - created_at > timedelta(minutes=30):
            db.delete_verification_code(code)
            return False, "⏰ **Verification code has expired.**\n\nCodes expire after 30 minutes. Please get a new one with `/getpremium`"
        
        db.delete_verification_code(code)
        
        LOGGER(__name__).info(f"User {user_id} successfully verified code {code}")
        return True, f"✅ **Verification successful!**\n\nYou now have **{PREMIUM_DURATION_MINUTES} minutes** of premium access!"
    
    def get_time_left(self, code: str) -> int:
        """Get minutes left for verification code"""
        code = code.upper().strip()
        
        verification_data = db.get_verification_code(code)
        if not verification_data:
            return 0
        
        created_at = verification_data['created_at']
        elapsed = datetime.now() - created_at
        remaining = timedelta(minutes=30) - elapsed
        
        if remaining.total_seconds() <= 0:
            return 0
        
        return int(remaining.total_seconds() / 60)
    
    def _build_ad_url(self, zone_id: str, user_hash: str) -> str:
        """Build Monetag ad URL"""
        if not zone_id:
            return ""
        
        # Monetag format: https://otieu.com/4/{zone_id}?subid={user_hash}
        return f"https://otieu.com/4/{zone_id}?subid={user_hash}"
    
    def generate_ad_link(self, user_id: int, bot_domain: str | None = None) -> tuple[str, str]:
        """Generate ad link with session ID - includes all configured ad slots (up to 10)"""
        import urllib.parse
        
        session_id = self.create_ad_session(user_id)
        user_hash = hashlib.md5(str(user_id).encode()).hexdigest()[:8]
        
        # Build ad URLs for all configured slots
        ad_urls = {}
        configured_slots = []
        
        for slot in range(1, 11):
            zone_id = self._get_random_zone_id(slot)
            if zone_id:
                ad_urls[f'ad{slot}'] = self._build_ad_url(zone_id, user_hash)
                configured_slots.append(slot)
        
        LOGGER(__name__).info(f"Generated Monetag ad links for user {user_id} - Configured slots: {configured_slots}")
        
        if bot_domain:
            # Encode all ad URLs for the landing page
            params = f"session={session_id}"
            for slot, url in ad_urls.items():
                params += f"&{slot}_url={urllib.parse.quote(url)}"
            
            landing_page_url = f"{bot_domain}/watch-ad?{params}"
            return session_id, landing_page_url
        
        # Fallback: return first available ad URL
        for url in ad_urls.values():
            if url:
                return session_id, url
        
        return session_id, f"https://example.com/watch-ad?session={session_id}"
    
    def get_premium_expiry(self) -> datetime:
        return datetime.now() + timedelta(minutes=PREMIUM_DURATION_MINUTES)

ad_monetization = AdMonetization()

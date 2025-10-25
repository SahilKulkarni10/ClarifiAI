#!/usr/bin/env python3
"""
Minimal startup script for Render - checks environment before starting
"""
import os
import sys

def check_environment():
    """Check critical environment variables"""
    print("=" * 60)
    print("🚀 ClariFi AI - Startup Check")
    print("=" * 60)
    
    # Check PORT
    port = os.getenv("PORT")
    if port:
        print(f"✅ PORT: {port}")
    else:
        print("⚠️  PORT not set, using default 8000")
        os.environ["PORT"] = "8000"
    
    # Check MongoDB
    mongodb_url = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI")
    if mongodb_url:
        # Mask the password for security
        masked = mongodb_url.split("@")[1] if "@" in mongodb_url else "configured"
        print(f"✅ MONGODB_URL: ...@{masked}")
    else:
        print("⚠️  MONGODB_URL not set - database features will not work")
    
    # Check Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}...")
    else:
        print("⚠️  GEMINI_API_KEY not set - AI features will not work")
    
    # Check JWT Secret
    jwt_secret = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
    if jwt_secret and len(jwt_secret) >= 32:
        print(f"✅ JWT_SECRET_KEY: configured ({len(jwt_secret)} chars)")
    else:
        print("⚠️  JWT_SECRET_KEY not set or too short")
    
    print("=" * 60)
    print()

if __name__ == "__main__":
    check_environment()
    
    # Now start uvicorn
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    print(f"🎬 Starting uvicorn on 0.0.0.0:{port}")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=False
        )
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)

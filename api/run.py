#!/usr/bin/env python3
"""
Minimal startup script for Render - checks environment before starting
"""
import os
import sys
import traceback

def check_environment():
    """Check critical environment variables"""
    print("=" * 60, flush=True)
    print("🚀 ClariFi AI - Startup Check", flush=True)
    print("=" * 60, flush=True)
    
    # Check PORT
    port = os.getenv("PORT")
    if port:
        print(f"✅ PORT: {port}", flush=True)
    else:
        print("⚠️  PORT not set, using default 8000", flush=True)
        os.environ["PORT"] = "8000"
    
    # Check MongoDB
    mongodb_url = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI")
    if mongodb_url:
        # Mask the password for security
        masked = mongodb_url.split("@")[1] if "@" in mongodb_url else "configured"
        print(f"✅ MONGODB_URL: ...@{masked}", flush=True)
    else:
        print("⚠️  MONGODB_URL not set - database features will not work", flush=True)
    
    # Check Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}...", flush=True)
    else:
        print("⚠️  GEMINI_API_KEY not set - AI features will not work", flush=True)
    
    # Check JWT Secret
    jwt_secret = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
    if jwt_secret and len(jwt_secret) >= 32:
        print(f"✅ JWT_SECRET_KEY: configured ({len(jwt_secret)} chars)", flush=True)
    else:
        print("⚠️  JWT_SECRET_KEY not set or too short", flush=True)
    
    print("=" * 60, flush=True)
    print(flush=True)

if __name__ == "__main__":
    try:
        print("🔧 Starting ClariFi AI API...", flush=True)
        check_environment()
        
        # Test if we can import main.app without errors
        print("📦 Testing app import...", flush=True)
        try:
            from main import app
            print("✅ App imported successfully!", flush=True)
        except Exception as import_error:
            print(f"❌ FAILED to import app: {import_error}", flush=True)
            traceback.print_exc()
            sys.exit(1)
        
        # Now start uvicorn
        import uvicorn
        
        port = int(os.getenv("PORT", 8000))
        print(f"🎬 Starting uvicorn on 0.0.0.0:{port}", flush=True)
        print(flush=True)
        
        uvicorn.run(
            app,  # Pass the app object directly instead of string
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=False
        )
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}", flush=True)
        print("=" * 60, flush=True)
        traceback.print_exc()
        print("=" * 60, flush=True)
        sys.exit(1)

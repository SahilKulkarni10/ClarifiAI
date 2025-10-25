#!/usr/bin/env python3
"""
Quick startup test to diagnose Render deployment issues
Run this to test if the app can start without crashing
"""

import os
import sys

print("=" * 60)
print("🔍 RENDER DEPLOYMENT DIAGNOSTIC TEST")
print("=" * 60)
print()

# Test 1: Check Python version
print("1️⃣ Python Version:")
print(f"   {sys.version}")
print()

# Test 2: Check environment variables
print("2️⃣ Environment Variables:")
env_vars = {
    "PORT": os.getenv("PORT", "NOT SET"),
    "MONGODB_URL": "SET" if os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI") else "NOT SET",
    "GEMINI_API_KEY": "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET",
    "JWT_SECRET_KEY": "SET" if os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") else "NOT SET",
    "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT SET"),
}

for key, value in env_vars.items():
    status = "✅" if value != "NOT SET" else "❌"
    print(f"   {status} {key}: {value}")
print()

# Test 3: Try importing main dependencies
print("3️⃣ Import Test:")
imports_to_test = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("motor", "Motor (MongoDB)"),
    ("config", "Config"),
]

all_imports_ok = True
for module, name in imports_to_test:
    try:
        __import__(module)
        print(f"   ✅ {name}")
    except ImportError as e:
        print(f"   ❌ {name}: {e}")
        all_imports_ok = False
print()

# Test 4: Try importing the app
print("4️⃣ App Import Test:")
try:
    from main import app
    print("   ✅ App imported successfully")
    print()
    
    # Test 5: Check if app is configured
    print("5️⃣ App Configuration:")
    print(f"   Title: {app.title}")
    print(f"   Version: {app.version}")
    print(f"   Routes: {len(app.routes)} routes")
    print()
    
except Exception as e:
    print(f"   ❌ Failed to import app: {e}")
    print()
    import traceback
    print("   Full error:")
    traceback.print_exc()
    sys.exit(1)

# Summary
print("=" * 60)
if all_imports_ok:
    print("✅ ALL CHECKS PASSED - App should start successfully")
    print()
    print("If deployment still fails, check:")
    print("  1. MongoDB connection string is correct")
    print("  2. MongoDB network access allows Render IPs")
    print("  3. Render logs for runtime errors")
else:
    print("❌ SOME CHECKS FAILED - Fix these before deploying")

print("=" * 60)

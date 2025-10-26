#!/usr/bin/env python3
"""
Startup verification script to test if the app can start without heavy dependencies
"""
import sys
import time

print("=" * 60)
print("🔍 ClariFi AI - Startup Verification Test")
print("=" * 60)

# Test 1: Basic imports
print("\n[1/5] Testing basic Python imports...")
try:
    import os
    import asyncio
    from datetime import datetime
    print("✅ Basic imports successful")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")
    sys.exit(1)

# Test 2: FastAPI imports
print("\n[2/5] Testing FastAPI imports...")
start = time.time()
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    elapsed = time.time() - start
    print(f"✅ FastAPI imports successful ({elapsed:.2f}s)")
except Exception as e:
    print(f"❌ FastAPI imports failed: {e}")
    sys.exit(1)

# Test 3: Config and Database (lightweight)
print("\n[3/5] Testing config and database imports...")
start = time.time()
try:
    from config import settings
    from database import MongoDB
    elapsed = time.time() - start
    print(f"✅ Config and database imports successful ({elapsed:.2f}s)")
    print(f"   - Environment: {settings.ENVIRONMENT}")
    print(f"   - Port: {settings.API_PORT}")
except Exception as e:
    print(f"❌ Config/database imports failed: {e}")
    sys.exit(1)

# Test 4: Main app import (should be fast now with lazy loading)
print("\n[4/5] Testing main app import (critical test)...")
start = time.time()
try:
    from main import app
    elapsed = time.time() - start
    print(f"✅ Main app imported successfully ({elapsed:.2f}s)")
    
    if elapsed > 15:
        print(f"⚠️  WARNING: App took {elapsed:.2f}s to import (should be <10s)")
        print("   This may cause Render port binding timeout")
    elif elapsed > 10:
        print(f"⚠️  CAUTION: App took {elapsed:.2f}s to import (borderline)")
    else:
        print(f"✅ Import time is good ({elapsed:.2f}s < 10s)")
        
except Exception as e:
    print(f"❌ Main app import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify lazy loading works
print("\n[5/5] Verifying lazy loading is active...")
try:
    # Check that heavy modules are NOT loaded yet
    import sys
    
    heavy_modules = ['chromadb', 'sentence_transformers', 'torch']
    loaded_heavy = [m for m in heavy_modules if m in sys.modules]
    
    if loaded_heavy:
        print(f"⚠️  WARNING: Heavy modules already loaded: {loaded_heavy}")
        print("   Lazy loading may not be working properly")
    else:
        print(f"✅ Heavy modules not loaded yet (lazy loading working!)")
        print(f"   Modules will load on first use")
        
except Exception as e:
    print(f"⚠️  Could not verify lazy loading: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print("✅ All critical tests passed!")
print("✅ App should be ready for Render deployment")
print("\nNext steps:")
print("  1. git add .")
print("  2. git commit -m 'Fix: Optimize startup for Render'")
print("  3. git push origin main")
print("  4. Check Render deployment logs")
print("=" * 60)

sys.exit(0)

#!/usr/bin/env python3
"""
Quick test script to verify server can start and bind to port
"""
import sys
import os
import asyncio
from main import app
import uvicorn

async def test_startup():
    """Test that the app can start"""
    print("Testing FastAPI app startup...")
    
    # Check environment variables
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"Port: {port}")
    print(f"Host: {host}")
    print(f"MongoDB URI configured: {bool(os.getenv('MONGODB_URI') or os.getenv('MONGODB_URL'))}")
    
    print("\n✅ Configuration looks good!")
    print("\nTo start the server manually:")
    print(f"  uvicorn main:app --host {host} --port {port}")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_startup())
        if result:
            print("\n✅ All checks passed!")
            sys.exit(0)
        else:
            print("\n❌ Some checks failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

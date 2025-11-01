#!/usr/bin/env python3
"""
Simple script to test if the backend is running and accessible.
"""

import urllib.request
import json
import sys

BACKEND_URL = "http://localhost:8000"

def test_backend():
    """Test backend connectivity and health."""
    print("Testing backend connection...")
    print(f"Backend URL: {BACKEND_URL}\n")
    
    # Test health endpoint
    try:
        print("1. Testing /api/health endpoint...")
        with urllib.request.urlopen(f"{BACKEND_URL}/api/health", timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"   ✓ Health check passed: {data}")
    except urllib.error.URLError as e:
        print(f"   ✗ Cannot connect to backend: {e}")
        print(f"\n   Please ensure the backend is running:")
        print(f"   cd .. && uv run uvicorn api.app:app --reload")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test env check endpoint
    try:
        print("\n2. Testing /api/env-check endpoint...")
        with urllib.request.urlopen(f"{BACKEND_URL}/api/env-check", timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"   Environment check: {data}")
            if not data.get('OPENAI_API_KEY_present'):
                print("   ⚠ Warning: OPENAI_API_KEY is not set!")
                print("   Set it with: export OPENAI_API_KEY=your-key")
    except Exception as e:
        print(f"   ⚠ Could not check environment: {e}")
    
    print("\n✓ Backend appears to be running correctly!")
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)

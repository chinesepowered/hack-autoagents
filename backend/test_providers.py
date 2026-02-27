"""Test script to verify sponsor API integrations."""

import asyncio
import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env from repo root (parent of backend/)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# Test data
TEST_TEXT = """
Good afternoon everyone. Total revenue for the quarter reached $110 billion, 
up 23% year over year. Our Services business continues to accelerate with 
over 1 billion paid subscriptions. We expect margin improvement in Q1.
"""


async def test_modulate():
    """Test Modulate Velma-2 API with a small audio sample."""
    api_key = os.getenv("MODULATE_API_KEY")
    if not api_key:
        print("❌ MODULATE: No API key set")
        return False

    print("🎤 MODULATE: Testing Velma-2 Batch API...")
    
    # Create a minimal test - just check if the endpoint responds
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Test with API key validation (no file upload)
            response = await client.post(
                "https://modulate-developer-apis.com/api/velma-2-stt-batch",
                headers={"X-API-Key": api_key},
                data={"speaker_diarization": "true", "emotion_signal": "true"},
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            # 400/422 means API is reachable but needs file (expected)
            # 401/403 means bad API key
            if response.status_code in [400, 422]:
                print("✅ MODULATE: API reachable, key valid (needs audio file)")
                return True
            elif response.status_code in [401, 403]:
                print("❌ MODULATE: Invalid API key")
                return False
            else:
                print(f"⚠️ MODULATE: Unexpected status {response.status_code}")
                return True
    except Exception as e:
        print(f"❌ MODULATE: Error - {e}")
        return False


async def test_reka():
    """Test Reka Vision API with a simple text prompt."""
    api_key = os.getenv("REKA_API_KEY")
    if not api_key:
        print("❌ REKA: No API key set")
        return False

    print("👁️ REKA: Testing Vision API...")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.reka.ai/v1/chat",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "reka-flash",
                    "messages": [
                        {"role": "user", "content": "Say 'API test successful' in 5 words or less."}
                    ],
                },
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"   Response: {content[:100]}")
                print("✅ REKA: API working")
                return True
            elif response.status_code in [401, 403]:
                print(f"❌ REKA: Invalid API key - {response.text[:100]}")
                return False
            else:
                print(f"⚠️ REKA: Unexpected - {response.text[:200]}")
                return False
    except Exception as e:
        print(f"❌ REKA: Error - {e}")
        return False


async def test_fastino():
    """Test Fastino/Pioneer GLiNER2 API."""
    api_key = os.getenv("FASTINO_API_KEY")
    if not api_key:
        print("❌ FASTINO: No API key set")
        return False

    print("🏷️ FASTINO: Testing Pioneer API...")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Per llms.txt: Base URL is api.pioneer.ai, auth is Bearer JWT
            # Check if we can list deployments (validates auth)
            response = await client.get(
                "https://api.pioneer.ai/deployments",
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Deployments: {len(data) if isinstance(data, list) else data}")
                print("✅ FASTINO: API key valid, Pioneer connected")
                return True
            elif response.status_code in [401, 403]:
                print(f"❌ FASTINO: Invalid API key - {response.text[:100]}")
                return False
            else:
                print(f"⚠️ FASTINO: Status {response.status_code} - {response.text[:150]}")
                # 401 means auth issue, but other codes might still mean API is reachable
                return response.status_code not in [401, 403, 500]
    except Exception as e:
        print(f"❌ FASTINO: Error - {e}")
        return False


async def test_yutori():
    """Test Yutori Research API with a simple query."""
    api_key = os.getenv("YUTORI_API_KEY")
    if not api_key:
        print("❌ YUTORI: No API key set")
        return False

    print("🔍 YUTORI: Testing Research API...")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            # Per docs: X-API-KEY header, POST /v1/research/tasks
            response = await client.post(
                "https://api.yutori.com/v1/research/tasks",
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "query": "What is Apple Inc's stock ticker symbol?",
                },
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                data = response.json()
                print(f"   Response: {str(data)[:150]}...")
                print("✅ YUTORI: API working")
                return True
            elif response.status_code in [401, 403]:
                print(f"❌ YUTORI: Invalid API key - {response.text[:100]}")
                return False
            else:
                print(f"⚠️ YUTORI: Status {response.status_code} - {response.text[:200]}")
                return False
    except Exception as e:
        print(f"❌ YUTORI: Error - {e}")
        return False


async def main():
    print("=" * 60)
    print("EchoMind Provider API Tests")
    print("=" * 60)
    print()
    
    results = {
        "Modulate": await test_modulate(),
        "Reka": await test_reka(),
        "Fastino": await test_fastino(),
        "Yutori": await test_yutori(),
    }
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    for name, success in results.items():
        status = "✅ Working" if success else "❌ Failed"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    print()
    if all_passed:
        print("🎉 All APIs verified!")
    else:
        print("⚠️ Some APIs need attention")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

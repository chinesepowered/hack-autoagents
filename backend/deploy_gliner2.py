"""Test Pioneer API and find correct inference endpoint."""
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.getenv("FASTINO_API_KEY")
BASE_URL = "https://api.pioneer.ai"

if not API_KEY:
    print("ERROR: FASTINO_API_KEY not set in .env")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Check available base models
print("1. Checking base models at /inference/base-models...")
resp = httpx.get(f"{BASE_URL}/inference/base-models", headers=headers, timeout=30)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"   Models: {resp.json()}")
else:
    print(f"   Response: {resp.text[:300]}")

# Try direct inference endpoint
print("\n2. Testing /inference endpoint...")
payload = {
    "model_id": "gliner2-base",  # or might need full path
    "task": "ner",
    "text": "Tim Cook announced Apple's Q4 2024 revenue of $110 billion.",
    "labels": ["person", "company", "currency_amount", "date"],
}
resp = httpx.post(f"{BASE_URL}/inference", headers=headers, json=payload, timeout=30)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text[:500]}")

# Check felix deployments
print("\n3. Checking /felix/deployments...")
resp = httpx.get(f"{BASE_URL}/felix/deployments", headers=headers, timeout=30)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"   Deployments: {data}")
else:
    print(f"   Response: {resp.text[:300]}")

# Check felix models
print("\n4. Checking /felix/models...")
resp = httpx.get(f"{BASE_URL}/felix/models", headers=headers, timeout=30)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"   Models: {data}")
else:
    print(f"   Response: {resp.text[:300]}")

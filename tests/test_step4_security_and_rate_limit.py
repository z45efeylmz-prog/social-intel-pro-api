import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from config.settings import settings
from src.security.rate_limiter import rate_limiter
from src.main import app

client = TestClient(app)

def test_unit_rate_limiter():
    print("[TEST 1] Testing InMemoryRateLimiter sliding-window mechanics...")
    rate_limiter.reset()
    
    client_id = "test_user_unit"
    limit = 3
    
    # 3 requests allowed
    for i in range(3):
        allowed, remaining, _ = rate_limiter.check_rate_limit(client_id, max_requests=limit, window_seconds=60)
        assert allowed is True, f"Request {i+1} should be allowed"
        assert remaining == limit - (i + 1)
        
    # 4th request must be rejected
    allowed, remaining, retry_after = rate_limiter.check_rate_limit(client_id, max_requests=limit, window_seconds=60)
    assert allowed is False, "4th request should exceed limit"
    assert remaining == 0
    assert retry_after > 0
    print(f"  [PASS] Unit rate limiter enforced: rejected 4th request (retry_after={retry_after}s)")

def test_public_routes_bypass_security():
    print("\n[TEST 2] Testing whitelisted public routes (health/docs)...")
    resp_root = client.get("/")
    assert resp_root.status_code == 200
    assert resp_root.json()["status"] == "ONLINE"

    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    print("  [PASS] Root and /health accessible without auth restrictions.")

def test_pro_api_key_header():
    print("\n[TEST 3] Testing Master/Pro API Key authentication...")
    rate_limiter.reset()
    headers = {"X-API-Key": settings.MASTER_API_KEY}
    resp = client.get("/v1/niche-leaders?niche=tech", headers=headers)
    assert resp.status_code == 200
    assert resp.headers.get("X-Subscription-Tier") == "pro"
    assert resp.headers.get("X-RateLimit-Limit") == str(settings.RATE_LIMIT_PRO_PER_MINUTE)
    print(f"  [PASS] Pro Key recognized! Tier: {resp.headers.get('X-Subscription-Tier')}, Limit: {resp.headers.get('X-RateLimit-Limit')} req/min")

def test_rapidapi_proxy_secret():
    print("\n[TEST 4] Testing RapidAPI Gateway Proxy Secret integration...")
    rate_limiter.reset()
    # Temporarily set test rapidapi secret
    settings.RAPIDAPI_PROXY_SECRET = "rapidapi_secret_test_xyz123"
    try:
        headers = {
            "x-rapidapi-proxy-secret": "rapidapi_secret_test_xyz123",
            "x-rapidapi-user": "enterprise_agency_customer"
        }
        resp = client.get("/v1/niche-leaders?niche=fitness", headers=headers)
        assert resp.status_code == 200
        assert resp.headers.get("X-Subscription-Tier") == "rapidapi"
        print(f"  [PASS] RapidAPI Proxy Secret verified! Tier: {resp.headers.get('X-Subscription-Tier')}")
    finally:
        settings.RAPIDAPI_PROXY_SECRET = ""

def test_free_tier_rate_limit_enforcement():
    print("\n[TEST 5] Testing Free Tier Rate Limit 429 Too Many Requests...")
    rate_limiter.reset()
    # Set tight limit for quick test
    original_limit = settings.RATE_LIMIT_FREE_PER_MINUTE
    settings.RATE_LIMIT_FREE_PER_MINUTE = 4
    try:
        # First 4 requests should succeed
        for i in range(4):
            resp = client.get("/v1/niche-leaders?niche=tech")
            assert resp.status_code == 200, f"Request {i+1} failed"
            assert resp.headers.get("X-Subscription-Tier") == "free"
        
        # 5th request should trigger 429
        blocked = client.get("/v1/niche-leaders?niche=tech")
        assert blocked.status_code == 429, f"Expected 429, got {blocked.status_code}"
        data = blocked.json()
        assert data.get("error") == "rate_limit_exceeded"
        assert "retry_after_seconds" in data
        assert "Retry-After" in blocked.headers
        print(f"  [PASS] 429 Too Many Requests successfully returned!")
        print(f"  Error message: {data['message']}")
        print(f"  Retry-After header: {blocked.headers['Retry-After']}s")
    finally:
        settings.RATE_LIMIT_FREE_PER_MINUTE = original_limit
        rate_limiter.reset()

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 4 VERIFICATION: SECURITY, RATE LIMITER & RAPIDAPI GUARD")
    print("=" * 60)
    test_unit_rate_limiter()
    test_public_routes_bypass_security()
    test_pro_api_key_header()
    test_rapidapi_proxy_secret()
    test_free_tier_rate_limit_enforcement()
    print("=" * 60)
    print("ALL STEP 4 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

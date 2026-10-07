import sys
import os
import asyncio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from src.main import app
from src.analytics.competitor_spy import competitor_spy

def test_competitor_spy_direct():
    print("[TEST 1] Testing CompetitorSpy Python service directly...")
    result = asyncio.run(competitor_spy.compare_creators("mkbhd", "techlead", "instagram"))
    
    assert "winner_username" in result, "Missing winner_username"
    assert "creator_a" in result, "Missing creator_a"
    assert "creator_b" in result, "Missing creator_b"
    assert "agency_verdict" in result, "Missing agency_verdict"
    assert result["winner_username"] in ["mkbhd", "techlead"], f"Unexpected winner: {result['winner_username']}"
    
    print(f"  [PASS] Direct compare successful!")
    print(f"  Winner: @{result['winner_username']}")
    print(f"  ER Advantage: %{result['engagement_advantage_pct']}")
    print(f"  Authenticity Diff: {result['authenticity_advantage_points']} pts")
    print(f"  Verdict: {result['agency_verdict'][:75]}...")

def test_competitor_spy_endpoint():
    print("\n[TEST 2] Testing FastAPI GET /v1/competitor/compare endpoint...")
    client = TestClient(app)
    response = client.get("/v1/competitor/compare?creator_a=mkbhd&creator_b=techlead&platform=instagram")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    assert data["winner_username"] in ["mkbhd", "techlead"]
    assert "creator_a" in data
    assert "creator_b" in data
    assert data["creator_a"]["username"] == "mkbhd"
    assert data["creator_b"]["username"] == "techlead"
    assert data["engagement_advantage_pct"] >= 0
    assert data["authenticity_advantage_points"] >= 0
    assert len(data["agency_verdict"]) > 10
    
    print(f"  [PASS] Endpoint response status 200 OK")
    print(f"  Creator A: @{data['creator_a']['username']} (ER: %{data['creator_a']['engagement_rate_pct']}, Auth: {data['creator_a']['authenticity_score']}/100)")
    print(f"  Creator B: @{data['creator_b']['username']} (ER: %{data['creator_b']['engagement_rate_pct']}, Auth: {data['creator_b']['authenticity_score']}/100)")
    print(f"  Winner: @{data['winner_username']}")

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 3 VERIFICATION: COMPETITOR SPY & A/B COMPARATOR")
    print("=" * 60)
    test_competitor_spy_direct()
    test_competitor_spy_endpoint()
    print("=" * 60)
    print("ALL STEP 3 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

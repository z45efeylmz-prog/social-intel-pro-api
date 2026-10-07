import sys
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from config.settings import settings
from src.database.db import db
from src.security.rate_limiter import rate_limiter
from src.main import app

client = TestClient(app)

def run_comprehensive_suite():
    rate_limiter.reset()
    start_time = time.time()
    passed_tests = 0
    total_tests = 11

    print("=" * 75)
    print("EXPANDED MASTER INTEGRATION SUITE: SOCIAL INTEL PRO B2B MICRO-API")
    print("=" * 75)

    # 1. System Health Check
    print("\n[SUITE 1/11] Verifying API Server & Health Status...")
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    passed_tests += 1
    print("  [PASS] Server is healthy and responsive.")

    # 2. Viral Trends Harvesting
    print("\n[SUITE 2/11] Testing Viral Trends & Audio Radar Harvesting...")
    resp = client.get("/v1/viral-trends?platform=tiktok&niche=tech")
    assert resp.status_code == 200
    data = resp.json()
    assert "trending_sounds" in data and len(data["trending_sounds"]) > 0
    assert "trending_hashtags" in data and len(data["trending_hashtags"]) > 0
    sound_top = data["trending_sounds"][0]
    passed_tests += 1
    print(f"  [PASS] Harvested {len(data['trending_sounds'])} viral sounds & {len(data['trending_hashtags'])} hashtags.")
    print(f"         Top Viral Audio: '{sound_top['title']}' (Velocity: +%{sound_top['velocity_24h_pct']}, Breakout: {sound_top['is_breakout']})")

    # 3. Influencer Audit & Bot Detection
    print("\n[SUITE 3/11] Testing Influencer Deep Audit & Fake Follower Analysis...")
    resp = client.get("/v1/influencer/audit?username=mkbhd&platform=instagram")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "mkbhd"
    assert "metrics" in data
    assert 0 <= data["authenticity_score"] <= 100
    passed_tests += 1
    print(f"  [PASS] Creator @{data['username']} audited successfully.")
    print(f"         Followers: {data['metrics']['followers']:,} | ER: %{data['metrics']['engagement_rate_pct']} | Authenticity: {data['authenticity_score']}/100")

    # 4. Niche Leaders Directory
    print("\n[SUITE 4/11] Testing Niche Leaders Discovery Directory...")
    resp = client.get("/v1/niche-leaders?niche=finance")
    assert resp.status_code == 200
    data = resp.json()
    assert data["niche"] == "finance"
    assert len(data["creators"]) > 0
    passed_tests += 1
    print(f"  [PASS] Found {len(data['creators'])} verified high-performance finance creators.")

    # 5. AI Video Virality Predictor
    print("\n[SUITE 5/11] Testing AI Short-Form Video Virality Predictor...")
    payload = {
        "hook_text": "Nobody is talking about this secret AI workflow that billionaires use in 2026",
        "duration_seconds": 18,
        "niche": "tech",
        "target_platform": "tiktok",
        "has_trending_audio": True
    }
    resp = client.post("/v1/video/virality-predictor", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    pred = resp.json()
    assert 0 <= pred["virality_score"] <= 100
    assert "virality_tier" in pred
    assert len(pred["actionable_recommendations"]) > 0
    passed_tests += 1
    print(f"  [PASS] Virality Predictor returned: {pred['virality_score']}/100 ({pred['virality_tier']})")
    print(f"         Est. Completion Rate: %{pred['predicted_completion_rate_pct']} | Recommendations: {len(pred['actionable_recommendations'])}")

    # 6. Competitor Head-to-Head Spy
    print("\n[SUITE 6/11] Testing Competitor Head-to-Head Spy & Agency ROI Verdict...")
    resp = client.get("/v1/competitor/compare?creator_a=mkbhd&creator_b=techlead&platform=instagram")
    assert resp.status_code == 200
    comp = resp.json()
    assert comp["winner_username"] in ["mkbhd", "techlead"]
    assert "creator_a" in comp and "creator_b" in comp
    assert "agency_verdict" in comp
    passed_tests += 1
    print(f"  [PASS] Head-to-Head spy completed. Winner: @{comp['winner_username']}")
    print(f"         Advantage: ER %{comp['engagement_advantage_pct']} | Auth Diff: {comp['authenticity_advantage_points']} pts")

    # 7. [NEW] Audience Demographics & Geography Estimation
    print("\n[SUITE 7/11] Testing Audience Demographics & Geography Estimation...")
    resp = client.get("/v1/influencer/demographics?username=mkbhd&platform=instagram&niche=tech")
    assert resp.status_code == 200
    demo_res = resp.json()
    assert "demographics" in demo_res
    d = demo_res["demographics"]
    assert len(d["top_countries"]) > 0
    assert d["gender_split"]["male_pct"] > 0
    assert len(d["age_distribution"]) > 0
    passed_tests += 1
    print(f"  [PASS] Demographics estimated for @{demo_res['username']} (Lang: {d['primary_language']}, Confidence: {d['confidence_score']}/100)")
    print(f"         Top Country: {d['top_countries'][0]['country_name']} (%{d['top_countries'][0]['percentage']}) | Gender: %{d['gender_split']['male_pct']} Male")

    # 8. [NEW] 30-Day Growth Trajectory & Bot Spike Detector
    print("\n[SUITE 8/11] Testing 30-Day Follower History & Bot Spike Anomaly Detector...")
    resp = client.get("/v1/influencer/growth-history?username=mkbhd&platform=instagram&period_days=30")
    assert resp.status_code == 200
    growth_res = resp.json()
    assert growth_res["period_days"] == 30
    assert len(growth_res["history"]) == 30
    assert "bot_spike_detected" in growth_res
    passed_tests += 1
    print(f"  [PASS] Analyzed 30 days of growth for @{growth_res['username']}.")
    print(f"         Net Growth: +{growth_res['net_growth']:,} (+%{growth_res['growth_rate_pct']}) | Bot Spike: {growth_res['bot_spike_detected']}")
    print(f"         Verdict: {growth_res['growth_verdict'][:70]}...")

    # 9. [NEW] White-Label Agency Audit Dossier (HTML & Print)
    print("\n[SUITE 9/11] Testing White-Label Agency HTML/PDF Dossier Generator...")
    resp_html = client.get("/v1/influencer/audit/report?username=mkbhd&platform=instagram&format=html")
    assert resp_html.status_code == 200
    assert "text/html" in resp_html.headers.get("content-type", "")
    assert "INFLUENCER AUDIT DOSSIER" in resp_html.text
    assert "window.print()" in resp_html.text

    resp_json = client.get("/v1/influencer/audit/report?username=mkbhd&platform=instagram&format=json")
    assert resp_json.status_code == 200
    assert "audit" in resp_json.json()
    passed_tests += 1
    print("  [PASS] Agency Audit Dossier generated successfully in both HTML (print-ready) and JSON formats.")

    # 10. SQLite Persistence Verification
    print("\n[SUITE 10/11] Verifying SQLite Database Persistence...")
    cached_creator = db.get_creator("mkbhd")
    assert cached_creator is not None, "Creator should be persisted in SQLite"
    assert cached_creator["username"] == "mkbhd"
    passed_tests += 1
    print("  [PASS] SQLite persistence verified! Record loaded from local DB without network scraping.")

    # 11. Security & Rate Limiting Enforcement
    print("\n[SUITE 11/11] Verifying Security Gateway & RapidAPI Proxy Guard...")
    headers = {"X-API-Key": settings.MASTER_API_KEY}
    resp = client.get("/v1/viral-trends", headers=headers)
    assert resp.status_code == 200
    assert resp.headers.get("X-Subscription-Tier") == "pro"
    assert resp.headers.get("X-RateLimit-Limit") == str(settings.RATE_LIMIT_PRO_PER_MINUTE)
    passed_tests += 1
    print("  [PASS] Security Gateway operational. Pro tier authenticated successfully.")

    # Final summary
    duration = round(time.time() - start_time, 2)
    print("\n" + "=" * 75)
    print(f"EXPANDED MASTER TEST COMPLETED IN {duration}s")
    print(f"RESULT: {passed_tests}/{total_tests} MODULES PASSED (100% SUCCESS)")
    print("=" * 75)

if __name__ == "__main__":
    run_comprehensive_suite()

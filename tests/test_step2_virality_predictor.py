import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from src.main import app
from src.analytics.virality_predictor import virality_predictor
from src.models.schemas import ViralityPredictionRequest

client = TestClient(app)

def run_step2_tests():
    print("\n" + "="*65)
    print("   [ADIM 2 TESTI] YAPAY ZEKA DESTEKLI VIRALLIK TAHMINCISI")
    print("="*65)

    # 1. Test Weak Hook
    print("[*] 1. Zayif video kancasi ve uzun sure testi (Negative case)...")
    weak_req = ViralityPredictionRequest(
        hook_text="Hello guys, welcome to my daily vlog today",
        duration_seconds=65,
        niche="lifestyle",
        target_platform="tiktok",
        has_trending_audio=False
    )
    res_weak = virality_predictor.predict(weak_req)
    assert res_weak["virality_score"] < 50
    assert res_weak["virality_tier"] in ["AVERAGE_PERFORMANCE", "LOW_REACH"]
    print(f"    [PASS] Zayif Video Skoru: {res_weak['virality_score']}/100 (Kademe: {res_weak['virality_tier']})")
    print(f"           Tavsiye: {res_weak['actionable_recommendations'][0]}")

    # 2. Test Ultra-Viral Breakout Hook
    print("\n[*] 2. Guclu psikolojik kanca ve optimal sure testi (Positive case)...")
    strong_req = ViralityPredictionRequest(
        hook_text="Nobody is talking about this secret AI workflow that billionaires use...",
        duration_seconds=17,
        niche="tech",
        target_platform="tiktok",
        has_trending_audio=True
    )
    res_strong = virality_predictor.predict(strong_req)
    assert res_strong["virality_score"] >= 80
    assert res_strong["virality_tier"] == "VIRAL_BREAKOUT"
    assert res_strong["predicted_completion_rate_pct"] >= 75.0
    assert res_strong["estimated_reach_multiplier"] >= 4.0
    assert len(res_strong["detected_psychological_triggers"]) >= 2
    print(f"    [PASS] Viral Video Skoru: {res_strong['virality_score']}/100 (Kademe: {res_strong['virality_tier']})")
    print(f"           Tamamlanma Orani: %{res_strong['predicted_completion_rate_pct']}")
    print(f"           Erisim Carpani: {res_strong['estimated_reach_multiplier']}x")
    print(f"           Tetikleyiciler: {res_strong['detected_psychological_triggers']}")

    # 3. Test API Endpoint via HTTP POST
    print("\n[*] 3. FastAPI HTTP POST /v1/video/virality-predictor uctan uca testi...")
    payload = {
        "hook_text": "Stop making this 1 mistake before it's deleted...",
        "duration_seconds": 19,
        "niche": "finance",
        "target_platform": "instagram_reels",
        "has_trending_audio": True
    }
    api_resp = client.post("/v1/video/virality-predictor", json=payload)
    assert api_resp.status_code == 200
    data = api_resp.json()
    assert "virality_score" in data
    assert "optimal_posting_window_utc" in data
    print(f"    [PASS] HTTP 200 OK! Puan: {data['virality_score']}/100 (En iyi saat: {data['optimal_posting_window_utc']})")

    print("\n" + "="*65)
    print("   ADIM 2 TESTI BASARIYLA TAMAMLANDI! AI TAHMIN MOTORU AKTIF.")
    print("="*65 + "\n")

if __name__ == "__main__":
    run_step2_tests()

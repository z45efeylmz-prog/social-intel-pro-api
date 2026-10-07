import sys
import os
import asyncio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.harvester.live_scraper import live_scraper
from src.harvester.influencer_audit import influencer_auditor
from src.database.db import db

async def run_step1_tests():
    print("\n" + "="*65)
    print("   [ADIM 1 TESTI] CANLI VERI KAZIYICI & SQLITE VERITABANI")
    print("="*65)

    # 1. Test live scraper probe
    print("[*] 1. Canli ag kaziyicisi test ediliyor...")
    res = await live_scraper.fetch_public_profile("google", "instagram")
    assert "status" in res
    print(f"    [PASS] Canli Ag Durumu: {res['status']} (Hedef: google)")

    # 2. Test audit & database save
    print("[*] 2. Influencer analizi yapiliyor ve SQLite'a kaydediliyor...")
    audit = await influencer_auditor.audit_creator("test_creator_99", "instagram")
    assert audit["username"] == "test_creator_99"
    print(f"    [PASS] Analiz tamamlandi: ER=%{audit['metrics'].engagement_rate_pct}, Skor={audit['authenticity_score']}/100")

    # 3. Verify SQLite persistence
    print("[*] 3. SQLite veritabanindan geri okuma dogrulaniyor...")
    saved = db.get_creator("test_creator_99")
    assert saved is not None
    assert saved["username"] == "test_creator_99"
    assert saved["authenticity_score"] == audit["authenticity_score"]
    print(f"    [PASS] SQLite Kalicilik Dogrulandi: Kayit ID={saved['username']} (Risk: {saved['risk_level']})")

    # 4. Test trends database saving
    print("[*] 4. Trend sesler ve hashtag veritabani tablosu test ediliyor...")
    sample_sounds = [{
        "title": "Viral Anthem 2026", "author": "BeatLab", "video_count": 50000,
        "velocity_24h_pct": 85.5, "is_breakout": True, "audio_url": "https://test.com/a.mp3"
    }]
    sample_tags = [{
        "tag": "aiagents", "views_24h": 25000000, "growth_rate_pct": 92.0, "niche": "tech"
    }]
    db.save_trends(sample_sounds, sample_tags)
    recent = db.get_recent_sounds(limit=1)
    assert len(recent) > 0
    assert recent[0]["title"] == "Viral Anthem 2026"
    print(f"    [PASS] Trendler SQLite'a basariyla yazildi ve okundu (Ses: {recent[0]['title']})")

    print("="*65)
    print("   ADIM 1 TESTI BASARIYLA TAMAMLANDI! VERITABANI VE AG HAZIR.")
    print("="*65 + "\n")

if __name__ == "__main__":
    asyncio.run(run_step1_tests())

import re
import datetime
from typing import Dict, Any, List
from src.models.schemas import ViralityPredictionRequest, ViralityPredictionResponse

class ViralityPredictor:
    """
    AI-driven Short-form Video Virality Engine.
    Evaluates psychological hooks, retention length, and audio synergy.
    """

    PSYCHOLOGICAL_PATTERNS = {
        "Curiosity Gap": [r"nobody is talking", r"secret", r"hidden", r"what happened", r"this is why", r"truth about"],
        "Urgency / FOMO": [r"stop doing", r"before it's", r"right now", r"warning", r"mistake", r"don't make this"],
        "Authority & Proof": [r"tested", r"data shows", r"millionaire", r"billionaire", r"results", r"science"],
        "High Specificity": [r"\d+\s*(ways|tools|hacks|steps|rules|seconds|days|dollars|\$|%)"]
    }

    NICHE_OPTIMAL_HOURS = {
        "tech": "17:00 - 20:00 UTC",
        "finance": "14:00 - 17:00 UTC",
        "fitness": "06:00 - 09:00 UTC",
        "humor": "19:00 - 23:00 UTC",
        "lifestyle": "18:00 - 21:00 UTC"
    }

    def predict(self, req: ViralityPredictionRequest) -> Dict[str, Any]:
        hook = req.hook_text.lower().strip()
        score = 45 # Baseline average video score
        triggers_found = []
        recommendations = []

        # 1. Psychological Trigger Scoring
        for trigger_name, patterns in self.PSYCHOLOGICAL_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, hook):
                    triggers_found.append(trigger_name)
                    score += 12
                    break

        if not triggers_found:
            recommendations.append("Kanca Zayıf: İlk 3 saniyede izleyicide merak veya aciliyet uyandıracak kelimeler ('secret', 'stop doing', 'mistake') ekleyin.")
        else:
            recommendations.append(f"Güçlü Kanca: '{', '.join(triggers_found)}' tetikleyicisi başarıyla tespit edildi.")

        # 2. Duration / Loop Retention Optimization
        dur = req.duration_seconds
        if 11 <= dur <= 22:
            score += 18
            comp_rate = 82.0 + (score % 10)
            recommendations.append(f"Mükemmel Video Süresi ({dur}s): Algoritmik döngü (loop) oranı için en yüksek tatlı nokta (Sweet spot).")
        elif 23 <= dur <= 35:
            score += 8
            comp_rate = 68.0 + (score % 8)
        elif dur < 10:
            score -= 10
            comp_rate = 88.0
            recommendations.append("Video Çok Kısa (<10s): İzlenme süresi (watch-time) metriği zayıf kalabilir; süreyi en az 14 saniyeye çıkarın.")
        else: # > 35s
            score -= 12
            comp_rate = 42.0 + (score % 10)
            recommendations.append(f"Video Uzun ({dur}s): Kısa videolarda tam izlenme oranı kritik öneme sahiptir. Süreyi 20 saniye civarına kırpmayı deneyin.")

        # 3. Trending Audio Bonus
        if req.has_trending_audio:
            score += 15
            reach_mult = round(2.0 + (score / 25.0), 1)
        else:
            score -= 5
            reach_mult = round(1.0 + (score / 45.0), 1)
            recommendations.append("Trend Ses Yok: Videoyu son 24 saatte yükselen bir trend ses (viral audio) ile eşleştirmek keşfete çıkma hızını 2.5 kat arttırır.")

        # Score clamping
        score = max(15, min(98, score))

        # Virality Tier
        if score >= 82:
            tier = "VIRAL_BREAKOUT"
        elif score >= 65:
            tier = "HIGH_POTENTIAL"
        elif score >= 45:
            tier = "AVERAGE_PERFORMANCE"
        else:
            tier = "LOW_REACH"

        opt_hours = self.NICHE_OPTIMAL_HOURS.get(req.niche.lower(), "18:00 - 21:00 UTC")
        now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        return {
            "analyzed_at": now_str,
            "virality_score": score,
            "virality_tier": tier,
            "predicted_completion_rate_pct": round(comp_rate, 1),
            "estimated_reach_multiplier": reach_mult,
            "optimal_posting_window_utc": opt_hours,
            "detected_psychological_triggers": list(set(triggers_found)),
            "actionable_recommendations": recommendations
        }

virality_predictor = ViralityPredictor()

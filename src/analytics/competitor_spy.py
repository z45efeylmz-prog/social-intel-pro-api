import datetime
from typing import Dict, Any
from src.harvester.influencer_audit import influencer_auditor
from src.models.schemas import CreatorBrief, CompetitorCompareResponse

class CompetitorSpy:
    """
    Head-to-head Creator Spy & Agency ROI Comparator.
    Evaluates audience quality, engagement advantage, and sponsor ROI between two competing creators.
    """

    async def compare_creators(self, username_a: str, username_b: str, platform: str = "instagram") -> Dict[str, Any]:
        user_a = username_a.strip().replace("@", "").lower()
        user_b = username_b.strip().replace("@", "").lower()

        # Audit both creators
        data_a = await influencer_auditor.audit_creator(user_a, platform)
        data_b = await influencer_auditor.audit_creator(user_b, platform)

        m_a = data_a["metrics"]
        m_b = data_b["metrics"]

        er_a = m_a.engagement_rate_pct if hasattr(m_a, 'engagement_rate_pct') else m_a['engagement_rate_pct']
        er_b = m_b.engagement_rate_pct if hasattr(m_b, 'engagement_rate_pct') else m_b['engagement_rate_pct']

        f_a = m_a.followers if hasattr(m_a, 'followers') else m_a['followers']
        f_b = m_b.followers if hasattr(m_b, 'followers') else m_b['followers']

        auth_a = data_a["authenticity_score"]
        auth_b = data_b["authenticity_score"]

        # Calculate composite agency score: Authenticity (50%) + ER relative value (50%)
        composite_a = (auth_a * 0.5) + (er_a * 10.0 * 0.5)
        composite_b = (auth_b * 0.5) + (er_b * 10.0 * 0.5)

        er_diff = round(abs(er_a - er_b), 2)
        auth_diff = abs(auth_a - auth_b)

        if composite_a >= composite_b:
            winner = user_a
            adv_text = f"@{user_a}, @{user_b}'ye kıyasla daha yüksek kitle sadakatine ve organik etkileşime sahiptir."
        else:
            winner = user_b
            adv_text = f"@{user_b}, @{user_a}'ye kıyasla daha yüksek kitle sadakatine ve organik etkileşime sahiptir."

        verdict = (
            f"[WINNER]: @{winner}. {adv_text} "
            f"Farklar: Etkileşim farkı %{er_diff}, Güvenilirlik/Orijinallik farkı {auth_diff} puan. "
            f"Reklam bütçesi tahsisinde @{winner} öncelikli tercih edilmelidir."
        )

        creator_brief_a = CreatorBrief(
            username=user_a,
            followers=f_a,
            engagement_rate_pct=er_a,
            authenticity_score=auth_a,
            risk_level=data_a["risk_level"]
        )

        creator_brief_b = CreatorBrief(
            username=user_b,
            followers=f_b,
            engagement_rate_pct=er_b,
            authenticity_score=auth_b,
            risk_level=data_b["risk_level"]
        )

        return {
            "compared_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "creator_a": creator_brief_a,
            "creator_b": creator_brief_b,
            "winner_username": winner,
            "engagement_advantage_pct": er_diff,
            "authenticity_advantage_points": auth_diff,
            "agency_verdict": verdict
        }

competitor_spy = CompetitorSpy()

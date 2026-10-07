import datetime
from typing import Dict, Any

class AgencyReportGenerator:
    """
    Generates an executive, white-label, print-ready HTML/PDF Influencer Audit Dossier.
    """

    def generate_html_report(
        self,
        audit_data: Dict[str, Any],
        demographics_data: Dict[str, Any],
        growth_data: Dict[str, Any]
    ) -> str:
        username = audit_data.get("username", "creator")
        platform = audit_data.get("platform", "instagram").upper()
        auth_score = audit_data.get("authenticity_score", 85)
        metrics = audit_data.get("metrics", {})
        
        followers = metrics.get("followers", 0) if isinstance(metrics, dict) else getattr(metrics, "followers", 0)
        er = metrics.get("engagement_rate_pct", 0.0) if isinstance(metrics, dict) else getattr(metrics, "engagement_rate_pct", 0.0)
        avg_likes = metrics.get("average_likes", 0) if isinstance(metrics, dict) else getattr(metrics, "average_likes", 0)
        risk_level = audit_data.get("risk_level", "LOW")
        recommendation = audit_data.get("commercial_recommendation", "")
        
        demo = demographics_data.get("demographics", {})
        top_countries = demo.get("top_countries", [])
        gender = demo.get("gender_split", {})
        male_pct = gender.get("male_pct", 50.0)
        female_pct = gender.get("female_pct", 50.0)
        
        bot_spike = growth_data.get("bot_spike_detected", False)
        growth_verdict = growth_data.get("growth_verdict", "")

        # Color schemes based on score
        if auth_score >= 75:
            score_color = "#10b981" # Green
            badge_text = "VERIFIED SAFE / HIGH QUALITY"
        elif auth_score >= 50:
            score_color = "#f59e0b" # Yellow
            badge_text = "MODERATE RISK"
        else:
            score_color = "#ef4444" # Red
            badge_text = "HIGH RISK / SUSPECTED FAKE"

        # Format countries rows
        countries_html = ""
        for c in top_countries[:4]:
            c_name = c.get("country_name") if isinstance(c, dict) else c.country_name
            c_pct = c.get("percentage") if isinstance(c, dict) else c.percentage
            countries_html += f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px;">
                <span>{c_name}</span>
                <span style="font-weight: 600;">%{c_pct}</span>
            </div>
            """

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Dossier: @{username} | SocialIntel Pro</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .dossier-card {{
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 16px;
            max-width: 800px;
            width: 100%;
            padding: 36px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 24px;
            margin-bottom: 28px;
        }}
        .title-h1 {{
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin: 0 0 4px 0;
            color: #38bdf8;
        }}
        .subtitle {{
            color: #94a3b8;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .score-pill {{
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid {score_color};
            color: {score_color};
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 14px;
            font-weight: 700;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }}
        .metric-box {{
            background-color: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }}
        .metric-val {{
            font-size: 22px;
            font-weight: 800;
            color: #f1f5f9;
        }}
        .metric-label {{
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: 700;
            color: #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 14px;
            border-left: 3px solid #38bdf8;
            padding-left: 10px;
        }}
        .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }}
        .card-inner {{
            background-color: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
        }}
        .verdict-box {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border: 1px solid #38bdf8;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 28px;
        }}
        .print-btn {{
            background-color: #38bdf8;
            color: #0f172a;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 700;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .print-btn:hover {{
            background-color: #0284c7;
            color: #ffffff;
        }}
        @media print {{
            body {{ background-color: #ffffff; color: #000000; padding: 0; }}
            .dossier-card {{ border: none; box-shadow: none; background: #ffffff; color: #000000; }}
            .metric-box, .card-inner, .verdict-box {{ border: 1px solid #ccc; background: #fafafa; color: #000; }}
            .print-btn {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="dossier-card">
        <div class="header">
            <div>
                <h1 class="title-h1">@{username}</h1>
                <div class="subtitle">{platform} INFLUENCER AUDIT DOSSIER | CONFIDENTIAL</div>
            </div>
            <div style="text-align: right;">
                <div class="score-pill">{badge_text}</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 6px;">
                    Authenticity: <strong style="color: {score_color}; font-size: 14px;">{auth_score}/100</strong>
                </div>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-box">
                <div class="metric-val">{followers:,}</div>
                <div class="metric-label">Followers</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">%{er}</div>
                <div class="metric-label">Engagement Rate</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{avg_likes:,}</div>
                <div class="metric-label">Avg. Likes</div>
            </div>
            <div class="metric-box">
                <div class="metric-val" style="color: {'#10b981' if risk_level == 'LOW' else '#f59e0b'};">{risk_level}</div>
                <div class="metric-label">Commercial Risk</div>
            </div>
        </div>

        <div class="two-col">
            <div class="card-inner">
                <div class="section-title">Audience Demographics</div>
                <div style="margin-bottom: 12px; font-size: 13px; color: #94a3b8;">
                    Gender Split: <strong style="color: #f1f5f9;">%{male_pct} Male / %{female_pct} Female</strong>
                </div>
                {countries_html}
            </div>

            <div class="card-inner">
                <div class="section-title">Growth & Bot Detection</div>
                <div style="font-size: 13px; margin-bottom: 8px;">
                    Bot Spike Anomaly: <strong style="color: {'#ef4444' if bot_spike else '#10b981'};">{'DETECTED' if bot_spike else 'NONE (Clean)'}</strong>
                </div>
                <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5;">
                    {growth_verdict}
                </div>
            </div>
        </div>

        <div class="verdict-box">
            <div class="section-title" style="color: #38bdf8;">Strategic Agency Verdict</div>
            <div style="font-size: 14px; line-height: 1.6; color: #e2e8f0;">
                {recommendation}
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #334155; padding-top: 18px;">
            <div style="font-size: 11px; color: #64748b;">
                Report Date: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | SocialIntel Pro B2B Engine
            </div>
            <button class="print-btn" onclick="window.print()">Export to PDF / Print</button>
        </div>
    </div>
</body>
</html>"""
        return html_template

agency_report_generator = AgencyReportGenerator()

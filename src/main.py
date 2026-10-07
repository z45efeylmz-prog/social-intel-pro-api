import datetime
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder

from config.settings import settings
from src.cache.memory_cache import cache
from src.models.schemas import (
    ViralTrendsResponse,
    InfluencerAuditResponse,
    NicheLeadersResponse,
    NicheLeader,
    ViralityPredictionRequest,
    ViralityPredictionResponse,
    CompetitorCompareResponse,
    DemographicsResponse,
    HistoricalGrowthResponse
)
from src.harvester.trend_harvester import trend_harvester
from src.harvester.influencer_audit import influencer_auditor
from src.analytics.virality_predictor import virality_predictor
from src.analytics.competitor_spy import competitor_spy
from src.analytics.demographics import demographics_estimator
from src.analytics.historical_growth import historical_growth_analyzer
from src.reports.agency_report import agency_report_generator
from src.security.rate_limiter import RapidAPISecurityMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# RapidAPI Security & Rate Limiting Middleware
app.add_middleware(RapidAPISecurityMiddleware)

# CORS setup for frontend / web integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["General"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ONLINE",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "documentation": "/docs",
        "endpoints": {
            "viral_trends": "/v1/viral-trends?platform=all&niche=tech",
            "influencer_audit": "/v1/influencer/audit?username=mkbhd&platform=instagram",
            "niche_leaders": "/v1/niche-leaders?niche=fitness"
        }
    }

@app.get("/health", tags=["General"])
async def health():
    return {"status": "healthy", "service": settings.APP_NAME}

@app.get(
    "/v1/viral-trends",
    response_model=ViralTrendsResponse,
    tags=["Viral Radar"],
    summary="Get Breakout Audio & Viral Hashtags",
    description="Returns trending sounds with 24-hour growth velocity, high-retention video hook formulas, and fast-rising hashtags."
)
async def get_viral_trends(
    platform: str = Query("all", description="Source platform: 'tiktok', 'instagram', or 'all'"),
    niche: str = Query("all", description="Content category: 'tech', 'fitness', 'finance', 'lifestyle', or 'all'")
):
    cache_key = f"trends_{platform}_{niche}"
    cached_data = cache.get(cache_key)
    if cached_data:
        cached_data["cached"] = True
        return cached_data

    try:
        data = await trend_harvester.get_viral_trends(platform=platform, niche=niche)
        cache.set(cache_key, data, ttl_seconds=settings.CACHE_DEFAULT_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to harvest viral trends: {str(e)}")

@app.get(
    "/v1/influencer/audit",
    response_model=InfluencerAuditResponse,
    tags=["Influencer Intelligence"],
    summary="Audit Creator Authenticity & Engagement",
    description="Analyzes follower quality, true Engagement Rate (ER), bot probability, and commercial advertising safety."
)
async def audit_influencer(
    username: str = Query(..., description="Creator username/handle (without @)", examples=["cristiano"]),
    platform: str = Query("instagram", description="Target platform: 'instagram', 'tiktok', 'youtube'")
):
    clean_username = username.strip().replace("@", "").lower()
    if not clean_username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    cache_key = f"audit_{clean_username}_{platform}"
    cached_data = cache.get(cache_key)
    if cached_data:
        cached_data["cached"] = True
        return cached_data

    try:
        data = await influencer_auditor.audit_creator(username=clean_username, platform=platform)
        cache.set(cache_key, data, ttl_seconds=settings.CACHE_DEFAULT_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to audit influencer: {str(e)}")

@app.get(
    "/v1/niche-leaders",
    response_model=NicheLeadersResponse,
    tags=["Discovery"],
    summary="Discover Top Creators by Niche",
    description="Returns verified fast-growing micro & macro creators filtered by category."
)
async def get_niche_leaders(
    niche: str = Query("tech", description="Category: 'tech', 'fitness', 'finance', 'fashion'")
):
    niche_clean = niche.lower().strip()
    cache_key = f"leaders_{niche_clean}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Curated high-performance database by category
    db = {
        "tech": [
            NicheLeader(rank=1, username="techlead", niche="tech", followers=1420000, engagement_rate_pct=4.12, viral_score=94),
            NicheLeader(rank=2, username="mkbhd", niche="tech", followers=4900000, engagement_rate_pct=3.85, viral_score=98),
            NicheLeader(rank=3, username="codecraft", niche="tech", followers=215000, engagement_rate_pct=6.45, viral_score=89),
        ],
        "fitness": [
            NicheLeader(rank=1, username="hybrid_athlete", niche="fitness", followers=480000, engagement_rate_pct=7.10, viral_score=96),
            NicheLeader(rank=2, username="iron_nutrition", niche="fitness", followers=890000, engagement_rate_pct=4.95, viral_score=91),
            NicheLeader(rank=3, username="mobility_coach", niche="fitness", followers=140000, engagement_rate_pct=8.40, viral_score=93),
        ],
        "finance": [
            NicheLeader(rank=1, username="market_insights", niche="finance", followers=650000, engagement_rate_pct=3.90, viral_score=90),
            NicheLeader(rank=2, username="quant_investor", niche="finance", followers=310000, engagement_rate_pct=5.75, viral_score=95),
            NicheLeader(rank=3, username="wealth_blueprint", niche="finance", followers=185000, engagement_rate_pct=6.80, viral_score=92),
        ]
    }

    creators = db.get(niche_clean, db["tech"])
    res = {
        "niche": niche_clean,
        "updated_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_found": len(creators),
        "creators": creators
    }
    cache.set(cache_key, res, ttl_seconds=600)
    return res

@app.post(
    "/v1/video/virality-predictor",
    response_model=ViralityPredictionResponse,
    tags=["AI Predictive Intelligence"],
    summary="Predict Short-Form Video Virality & Loop Retention",
    description="Analyzes psychological hook power, duration loop dynamics, and audio synergy to forecast virality score (0-100)."
)
async def predict_video_virality(request: ViralityPredictionRequest):
    try:
        return virality_predictor.predict(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virality prediction failed: {str(e)}")

@app.get(
    "/v1/competitor/compare",
    response_model=CompetitorCompareResponse,
    tags=["Influencer Intelligence"],
    summary="Compare Two Competing Creators Head-to-Head",
    description="Performs an algorithmic A/B audience quality comparison and provides agency sponsorship recommendation."
)
async def compare_competitors(
    creator_a: str = Query(..., description="First creator handle", examples=["mkbhd"]),
    creator_b: str = Query(..., description="Second creator handle", examples=["techlead"]),
    platform: str = Query("instagram", description="Target platform: 'instagram', 'tiktok'")
):
    try:
        return await competitor_spy.compare_creators(creator_a, creator_b, platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Competitor comparison failed: {str(e)}")

@app.get(
    "/v1/influencer/demographics",
    response_model=DemographicsResponse,
    tags=["Influencer Intelligence"],
    summary="Estimate Audience Demographics & Geography",
    description="Algorithmic estimation of audience geographic distribution, gender split, and age brackets based on creator signals."
)
async def get_influencer_demographics(
    username: str = Query(..., description="Creator username", examples=["mkbhd"]),
    platform: str = Query("instagram", description="Target platform: 'instagram', 'tiktok', 'youtube'"),
    niche: str = Query("tech", description="Category: tech, finance, beauty, fitness, etc.")
):
    clean_username = username.strip().replace("@", "").lower()
    cache_key = f"demo_{clean_username}_{platform}_{niche}"
    cached = cache.get(cache_key)
    if cached:
        cached["cached"] = True
        return cached

    try:
        res = demographics_estimator.estimate(username=clean_username, platform=platform, niche=niche)
        cache.set(cache_key, res.dict() if hasattr(res, 'dict') else res, ttl_seconds=600)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to estimate demographics: {str(e)}")

@app.get(
    "/v1/influencer/growth-history",
    response_model=HistoricalGrowthResponse,
    tags=["Influencer Intelligence"],
    summary="30-Day Follower History & Bot Spike Anomaly Detection",
    description="Tracks 30-day daily follower velocity, flags unnatural overnight bot spikes, and generates safety audit score."
)
async def get_growth_history(
    username: str = Query(..., description="Creator username", examples=["mkbhd"]),
    platform: str = Query("instagram", description="Platform"),
    period_days: int = Query(30, description="Period in days (7 to 90)", ge=7, le=90)
):
    clean_username = username.strip().replace("@", "").lower()
    cache_key = f"growth_{clean_username}_{period_days}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        # First get audit for baseline follower count & authenticity
        audit = await influencer_auditor.audit_creator(clean_username, platform)
        m = audit["metrics"]
        followers = m.followers if hasattr(m, 'followers') else m['followers']
        auth_score = audit["authenticity_score"]

        res = historical_growth_analyzer.analyze_growth(
            username=clean_username,
            current_followers=followers,
            authenticity_score=auth_score,
            platform=platform,
            period_days=period_days
        )
        cache.set(cache_key, res.dict() if hasattr(res, 'dict') else res, ttl_seconds=600)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate growth history: {str(e)}")

@app.get(
    "/v1/influencer/audit/report",
    tags=["Influencer Intelligence"],
    summary="Generate White-Label Audit Dossier (HTML / PDF Print)",
    description="Generates an executive, print-ready HTML/PDF white-label influencer audit report for marketing agencies and brand sponsors."
)
async def get_agency_audit_report(
    username: str = Query(..., description="Creator username", examples=["mkbhd"]),
    platform: str = Query("instagram", description="Platform: instagram, tiktok"),
    niche: str = Query("tech", description="Category: tech, fitness, finance, etc."),
    format: str = Query("html", description="Output format: 'html' (print-ready) or 'json'")
):
    clean_username = username.strip().replace("@", "").lower()
    try:
        audit_data = await influencer_auditor.audit_creator(clean_username, platform)
        demo_data = demographics_estimator.estimate(clean_username, platform, niche).dict()
        m = audit_data["metrics"]
        followers = m.followers if hasattr(m, 'followers') else m['followers']
        growth_data = historical_growth_analyzer.analyze_growth(
            clean_username,
            followers,
            audit_data["authenticity_score"],
            platform
        ).dict()

        if format.lower() == "html":
            html_content = agency_report_generator.generate_html_report(audit_data, demo_data, growth_data)
            return HTMLResponse(content=html_content, status_code=200)
        else:
            return JSONResponse(content=jsonable_encoder({
                "audit": audit_data,
                "demographics": demo_data,
                "growth_history": growth_data
            }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audit report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)

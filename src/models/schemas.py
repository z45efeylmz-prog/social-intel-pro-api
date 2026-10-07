from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TrendingSound(BaseModel):
    title: str = Field(..., description="Name/Title of the viral audio")
    author: str = Field(..., description="Original creator or artist")
    video_count: int = Field(..., description="Total videos made with this audio")
    velocity_24h_pct: float = Field(..., description="24-hour usage growth velocity percentage")
    is_breakout: bool = Field(..., description="Whether this sound is currently breaking out exponentially")
    audio_url: Optional[str] = Field(None, description="Direct preview or link to audio")

class TrendingHashtag(BaseModel):
    tag: str = Field(..., description="Hashtag string without #")
    views_24h: int = Field(..., description="Total views generated in the past 24 hours")
    growth_rate_pct: float = Field(..., description="Percentage growth over previous period")
    niche: str = Field(..., description="Primary category: fitness, finance, tech, fashion, humor")

class ViralTrendsResponse(BaseModel):
    platform: str = Field("all", description="Source platform: tiktok, instagram, all")
    generated_at: str
    cached: bool
    trending_sounds: List[TrendingSound]
    trending_hashtags: List[TrendingHashtag]
    viral_hooks_today: List[str] = Field(..., description="Top 5 psychological video hooks trending today")

class InfluencerMetrics(BaseModel):
    username: str
    platform: str
    followers: int
    following: int
    total_posts: int
    engagement_rate_pct: float = Field(..., description="Likes + Comments / Followers ratio")
    average_likes: int
    average_comments: int
    average_views: Optional[int] = None
    estimated_reach: int

class InfluencerAuditResponse(BaseModel):
    username: str
    platform: str
    analyzed_at: str
    cached: bool
    metrics: InfluencerMetrics
    authenticity_score: int = Field(..., description="0-100 score: >75 Genuine, <45 Suspected Bot/Fake followers")
    growth_status: str = Field(..., description="VIRAL_SURGE, STEADY_GROWTH, STAGNANT, LOSING_FOLLOWERS")
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH (Advertising risk)")
    commercial_recommendation: str = Field(..., description="Actionable recommendation for marketing brands/agencies")

class NicheLeader(BaseModel):
    rank: int
    username: str
    niche: str
    followers: int
    engagement_rate_pct: float
    viral_score: int

class NicheLeadersResponse(BaseModel):
    niche: str
    updated_at: str
    total_found: int
    creators: List[NicheLeader]

class ViralityPredictionRequest(BaseModel):
    hook_text: str = Field(..., description="First 3 seconds caption/hook text of the video", example="Nobody is talking about this secret AI tool...")
    duration_seconds: int = Field(18, description="Length of the short-form video in seconds", ge=3, le=300)
    niche: str = Field("tech", description="Category: tech, finance, fitness, humor, lifestyle")
    target_platform: str = Field("tiktok", description="tiktok, instagram_reels, youtube_shorts")
    has_trending_audio: bool = Field(True, description="Whether video pairs with breakout trending sound")

class ViralityPredictionResponse(BaseModel):
    analyzed_at: str
    virality_score: int = Field(..., description="0-100 predicted viral probability score")
    virality_tier: str = Field(..., description="VIRAL_BREAKOUT, HIGH_POTENTIAL, AVERAGE_PERFORMANCE, LOW_REACH")
    predicted_completion_rate_pct: float = Field(..., description="Expected percentage of viewers who watch to completion")
    estimated_reach_multiplier: float = Field(..., description="Expected view multiplier compared to account baseline (e.g. 3.5x)")
    optimal_posting_window_utc: str = Field(..., description="Highest-traffic algorithmic upload time window")
    detected_psychological_triggers: List[str]
    actionable_recommendations: List[str]

class CreatorBrief(BaseModel):
    username: str
    followers: int
    engagement_rate_pct: float
    authenticity_score: int
    risk_level: str

class CompetitorCompareResponse(BaseModel):
    compared_at: str
    creator_a: CreatorBrief
    creator_b: CreatorBrief
    winner_username: str = Field(..., description="The creator with superior ROI and audience quality")
    engagement_advantage_pct: float = Field(..., description="Difference in engagement rate")
    authenticity_advantage_points: int = Field(..., description="Difference in audience safety score")
    agency_verdict: str = Field(..., description="Clear strategic recommendation for sponsor brands")


class CountryShare(BaseModel):
    country_code: str
    country_name: str
    percentage: float

class AgeBracket(BaseModel):
    bracket: str
    percentage: float

class GenderShare(BaseModel):
    male_pct: float
    female_pct: float
    other_pct: float = 0.0

class AudienceDemographics(BaseModel):
    top_countries: List[CountryShare]
    gender_split: GenderShare
    age_distribution: List[AgeBracket]
    primary_language: str
    confidence_score: int

class DemographicsResponse(BaseModel):
    username: str
    platform: str
    analyzed_at: str
    cached: bool
    demographics: AudienceDemographics

class DailyGrowthPoint(BaseModel):
    date: str
    followers: int
    daily_change: int
    unnatural_spike: bool

class HistoricalGrowthResponse(BaseModel):
    username: str
    platform: str
    period_days: int
    analyzed_at: str
    baseline_followers: int
    current_followers: int
    net_growth: int
    growth_rate_pct: float
    bot_spike_detected: bool
    suspicious_dates: List[str]
    growth_verdict: str
    history: List[DailyGrowthPoint]

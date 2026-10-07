import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "SocialIntel Pro API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Real-time Social Media Trends, Viral Audio Radar, Influencer Authenticity & Virality Intelligence Engine."
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CACHE_DEFAULT_TTL: int = 300 # 5 minutes cache to avoid redundant scraping
    RAPIDAPI_PROXY_SECRET: str = os.getenv("RAPIDAPI_PROXY_SECRET", "")
    MASTER_API_KEY: str = os.getenv("MASTER_API_KEY", "social_intel_master_key_2026")
    RATE_LIMIT_FREE_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_FREE_PER_MINUTE", "10"))
    RATE_LIMIT_PRO_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PRO_PER_MINUTE", "120"))
    ENFORCE_AUTH: bool = os.getenv("ENFORCE_AUTH", "False").lower() in ("true", "1")

settings = Settings()

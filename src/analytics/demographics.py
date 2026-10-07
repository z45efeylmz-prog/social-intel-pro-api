import datetime
import re
from typing import Dict, Any, List
from src.models.schemas import (
    CountryShare,
    AgeBracket,
    GenderShare,
    AudienceDemographics,
    DemographicsResponse
)

class DemographicsEstimator:
    """
    Algorithmic Demographic & Audience Geography Estimation Engine.
    Infers gender split, geographic concentration, and age distribution using
    bio linguistic patterns, platform characteristics, and niche behavioral profiles.
    """

    NICHE_GENDER_PROFILES = {
        "tech": (68.0, 32.0),
        "finance": (74.0, 26.0),
        "gaming": (72.0, 28.0),
        "beauty": (18.0, 82.0),
        "fashion": (24.0, 76.0),
        "fitness": (53.0, 47.0),
        "lifestyle": (42.0, 58.0),
        "food": (45.0, 55.0)
    }

    PLATFORM_AGE_PROFILES = {
        "tiktok": [
            AgeBracket(bracket="18-24", percentage=48.0),
            AgeBracket(bracket="25-34", percentage=31.0),
            AgeBracket(bracket="35-44", percentage=14.0),
            AgeBracket(bracket="45+", percentage=7.0),
        ],
        "instagram": [
            AgeBracket(bracket="18-24", percentage=33.0),
            AgeBracket(bracket="25-34", percentage=45.0),
            AgeBracket(bracket="35-44", percentage=15.0),
            AgeBracket(bracket="45+", percentage=7.0),
        ],
        "youtube": [
            AgeBracket(bracket="18-24", percentage=29.0),
            AgeBracket(bracket="25-34", percentage=41.0),
            AgeBracket(bracket="35-44", percentage=20.0),
            AgeBracket(bracket="45+", percentage=10.0),
        ]
    }

    def estimate(
        self,
        username: str,
        platform: str = "instagram",
        niche: str = "tech",
        bio_text: str = ""
    ) -> DemographicsResponse:
        platform_clean = platform.lower().strip()
        niche_clean = niche.lower().strip()
        bio_lower = (bio_text or username).lower()

        # 1. Geographic & Linguistic Heuristics
        is_turkish = bool(
            re.search(r"(\.tr|istanbul|ankara|izmir|türkiye|turkey|iletisim|resmi)", bio_lower) or
            any(c in bio_lower for c in ["ç", "ğ", "ı", "ö", "ş", "ü"])
        )

        if is_turkish:
            primary_lang = "Turkish"
            top_countries = [
                CountryShare(country_code="TR", country_name="Turkey", percentage=68.5),
                CountryShare(country_code="DE", country_name="Germany", percentage=11.2),
                CountryShare(country_code="AZ", country_name="Azerbaijan", percentage=6.4),
                CountryShare(country_code="CY", country_name="Cyprus", percentage=3.8),
                CountryShare(country_code="OTHER", country_name="Other / Global", percentage=10.1)
            ]
            confidence = 88
        else:
            primary_lang = "English"
            top_countries = [
                CountryShare(country_code="US", country_name="United States", percentage=44.2),
                CountryShare(country_code="GB", country_name="United Kingdom", percentage=15.1),
                CountryShare(country_code="CA", country_name="Canada", percentage=9.8),
                CountryShare(country_code="DE", country_name="Germany", percentage=6.7),
                CountryShare(country_code="OTHER", country_name="Other / International", percentage=24.2)
            ]
            confidence = 82

        # 2. Gender Split
        male_pct, female_pct = self.NICHE_GENDER_PROFILES.get(niche_clean, (51.0, 49.0))
        gender_share = GenderShare(male_pct=male_pct, female_pct=female_pct, other_pct=0.0)

        # 3. Age Distribution
        age_dist = self.PLATFORM_AGE_PROFILES.get(platform_clean, self.PLATFORM_AGE_PROFILES["instagram"])

        demographics = AudienceDemographics(
            top_countries=top_countries,
            gender_split=gender_share,
            age_distribution=age_dist,
            primary_language=primary_lang,
            confidence_score=confidence
        )

        return DemographicsResponse(
            username=username.lower().replace("@", ""),
            platform=platform_clean,
            analyzed_at=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            cached=False,
            demographics=demographics
        )

demographics_estimator = DemographicsEstimator()

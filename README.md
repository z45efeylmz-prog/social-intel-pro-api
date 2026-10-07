# 📱 SocialIntel Pro API (Micro-API Engine)

> **Agency-grade Social Media Trends, Viral Audio Radar, and Influencer Authenticity Intelligence Engine.**

Built for **RapidAPI / AWS Data Exchange** monetization. Provides fast, sub-millisecond JSON endpoints for marketing agencies, AI video tool creators, and influencer management platforms.

---

## ⚡ Core Endpoints

1. **`GET /v1/viral-trends`**
   - Fetches breakout viral audio, 24-hour velocity growth, trending hashtags, and top 5 psychological video hooks.
   - Query params: `platform` (`tiktok`, `instagram`, `all`), `niche` (`tech`, `fitness`, `finance`, `lifestyle`).

2. **`GET /v1/influencer/audit`**
   - Audits any creator handle.
   - Calculates true Engagement Rate (ER), statistical Authenticity Score (0-100), Ghost/Bot follower risk level (`LOW`, `MODERATE`, `HIGH`), and commercial sponsorship recommendations.
   - Query params: `username`, `platform`.

3. **`GET /v1/niche-leaders`**
   - Discovers top trending micro & macro creators filtered by category.
   - Query params: `niche`.

4. **`GET /health`**
   - Standard health-check for RapidAPI gateway liveness monitoring.

---

## 🚀 How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API server
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Swagger documentation is available at:
👉 **`http://127.0.0.1:8000/docs`**
Interactive ReDoc documentation is available at:
👉 **`http://127.0.0.1:8000/redoc`**

---

## 💰 RapidAPI Pricing Structure

| Tier | Monthly Price | Request Quota | Target Audience |
| :--- | :---: | :---: | :--- |
| **Basic (Free)** | $0 / mo | 100 requests | Test & integration |
| **Pro** | $39 / mo | 10,000 requests | Solo creators & indie hackers |
| **Ultra** | $89 / mo | 100,000 requests | Marketing agencies & SaaS tools |
| **Mega** | $199 / mo | 1,000,000 requests | Enterprise automation pipelines |

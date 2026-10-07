import time
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from config.settings import settings

class InMemoryRateLimiter:
    """
    High-performance sliding-window rate limiter.
    Stores request epoch timestamps per client identifier.
    """
    def __init__(self):
        self._history: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, client_id: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - window_seconds
        
        # Clean older entries
        timestamps = [t for t in self._history[client_id] if t > window_start]
        self._history[client_id] = timestamps

        if len(timestamps) >= max_requests:
            oldest = timestamps[0]
            retry_after = max(1, int(oldest + window_seconds - now))
            return False, 0, retry_after

        # Record this request
        self._history[client_id].append(now)
        remaining = max_requests - len(self._history[client_id])
        return True, remaining, 0

    def reset(self, client_id: Optional[str] = None):
        """Helper to clear history (useful for unit tests)."""
        if client_id:
            self._history.pop(client_id, None)
        else:
            self._history.clear()

rate_limiter = InMemoryRateLimiter()

class RapidAPISecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware validating RapidAPI Proxy Secret, Custom API Keys, and enforcing sliding-window rate limits.
    Safe routes (/docs, /redoc, /openapi.json, /, /health) are whitelisted.
    """
    WHITELISTED_PATHS = {"/", "/docs", "/redoc", "/openapi.json", "/health", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Whitelist public docs and health endpoints
        if path in self.WHITELISTED_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Extract authentication headers
        rapidapi_secret = request.headers.get("x-rapidapi-proxy-secret")
        rapidapi_user = request.headers.get("x-rapidapi-user", "rapidapi_client")
        api_key = request.headers.get("x-api-key")
        auth_header = request.headers.get("authorization", "")

        bearer_key = None
        if auth_header.lower().startswith("bearer "):
            bearer_key = auth_header.split(" ", 1)[1].strip()

        effective_key = api_key or bearer_key

        is_rapidapi = False
        is_pro_key = False

        # Validate RapidAPI Secret if configured
        if settings.RAPIDAPI_PROXY_SECRET:
            if rapidapi_secret == settings.RAPIDAPI_PROXY_SECRET:
                is_rapidapi = True

        # Validate Direct Master / Pro API Key
        if effective_key and effective_key == settings.MASTER_API_KEY:
            is_pro_key = True

        # Determine Tier & Client Identifier
        if is_rapidapi:
            tier = "rapidapi"
            client_id = f"rapidapi:{rapidapi_user}"
            limit = settings.RATE_LIMIT_PRO_PER_MINUTE
        elif is_pro_key:
            tier = "pro"
            client_id = f"key:{effective_key[:8]}"
            limit = settings.RATE_LIMIT_PRO_PER_MINUTE
        else:
            # Check if strict auth is enforced
            if settings.ENFORCE_AUTH:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "unauthorized",
                        "message": "Valid X-API-Key or RapidAPI Proxy Secret required to access this endpoint."
                    }
                )
            tier = "free"
            client_ip = request.client.host if request.client else "unknown_ip"
            client_id = f"free_ip:{client_ip}"
            limit = settings.RATE_LIMIT_FREE_PER_MINUTE

        # Enforce Rate Limiting
        allowed, remaining, retry_after = rate_limiter.check_rate_limit(client_id, limit, window_seconds=60)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit reached ({limit} req/min). Please slow down or upgrade your subscription tier.",
                    "tier": tier,
                    "retry_after_seconds": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Process Request
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-Subscription-Tier"] = tier
        return response

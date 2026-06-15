from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class CORSMiddlewareCustom(BaseHTTPMiddleware):
    def __init__(self, app, allowed_origins):
        super().__init__(app)
        self.allowed_origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        if origin in self.allowed_origins:
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=60, window=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self._requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        import time

        client = request.client.host if request.client else "unknown"
        now = time.time()
        if client not in self._requests:
            self._requests[client] = []
        self._requests[client] = [t for t in self._requests[client] if now - t < self.window]
        if len(self._requests[client]) >= self.max_requests:
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        self._requests[client].append(now)
        return await call_next(request)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    XSS_PATTERNS = ["<script", "javascript:", "onload=", "onerror=", "onclick=", "onmouseover=", "expression(", "url(", "@import"]

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if body:
                    lower = body.lower().decode("utf-8", errors="ignore")
                    for pattern in self.XSS_PATTERNS:
                        if pattern in lower:
                            return JSONResponse(
                                status_code=400, content={"detail": "Potentially malicious input detected"}
                            )
            except Exception:
                pass
            request._body = body
        return await call_next(request)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.middleware import (
    CORSMiddlewareCustom,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    InputSanitizationMiddleware,
)


def create_app() -> FastAPI:
    app = FastAPI(title="Under 1000 API", version="1.0.0", redirect_slashes=False)

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(InputSanitizationMiddleware)
    app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
    app.add_middleware(CORSMiddlewareCustom, allowed_origins=settings.allowed_origins)

    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.get("/api/health")
    async def health():
        return {"status": "healthy", "env": settings.env}

    from app.routers import auth, products, cart, orders, admin

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(products.router, prefix="/api/products", tags=["products"])
    app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
    app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

    return app

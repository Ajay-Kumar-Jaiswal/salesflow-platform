from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.database.database import Base, engine
import app.models  # Registers all models with Base.metadata
from app.routers import (
    auth_router,
    users_router,
    customers_router,
    activities_router,
    opportunities_router,
    follow_ups_router,
    dashboard_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup (especially for development & test setups)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="SalesFlow CRM REST API - Enterprise Customer Relationship Management",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware with environment-configured origins (no wildcard '*')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# ==========================================
# Error Handling (Phase 18)
# ==========================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg')}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log securely without exposing database connection details or stack traces
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )


# ==========================================
# Route Registration
# ==========================================

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(activities_router, prefix=settings.API_V1_STR)
app.include_router(opportunities_router, prefix=settings.API_V1_STR)
app.include_router(follow_ups_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "2.0.0",
        "documentation": "/docs",
        "health": "/api/health",
    }


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

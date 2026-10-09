"""
FPMIS - Forensic Post-Mortem Intelligence System
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.models import create_tables
from app.routers import (
    auth_router, cases_router, autopsy_router, evidence_router,
    tod_router, decomposition_router, matching_router, alerts_router, search_router
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    print("🚀 Starting FPMIS Backend...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1]}")
    
    
    print("✅ FPMIS Backend Ready!")
    
    yield
    
    print("👋 Shutting down FPMIS Backend...")



app = FastAPI(
    title=settings.APP_NAME,
    description="""
    
    A unified digital platform for forensic post-mortem intelligence.
    
    1. **Autopsy Report Structuring** - Standardized documentation
    2. **Time-of-Death Estimation** - Rule-based TOD calculation
    3. **Decomposition Logging** - Environmental tracking
    4. **Chain-of-Custody** - Evidence tracking
    5. **Body Identification** - Missing person matching
    6. **Intelligence Database** - Searchable case database
    7. **Case Comparison** - Side-by-side analysis
    8. **Pattern Alerts** - Automated cluster detection
    
    Digital Care Crew
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    return response



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with cleaner format"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join([str(loc) for loc in error["loc"]]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": errors
        }
    )



app.include_router(auth_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(autopsy_router, prefix="/api")
app.include_router(evidence_router, prefix="/api")
app.include_router(tod_router, prefix="/api")
app.include_router(decomposition_router, prefix="/api")
app.include_router(matching_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(search_router, prefix="/api")



@app.get("/", tags=["Root"])
def root():
    """API Root - Health check"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "message": "Welcome to FPMIS API"
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


@app.get("/api", tags=["Root"])
def api_root():
    """API version info"""
    return {
        "version": settings.APP_VERSION,
        "endpoints": {
            "auth": "/api/auth - Register, Login, Logout",
            "cases": "/api/cases - Case management (CRUD)",
            "autopsy": "/api/cases/{id}/autopsy - Autopsy reports",
            "injuries": "/api/cases/{id}/injuries - Injury documentation",
            "evidence": "/api/cases/{id}/evidence - Evidence management",
            "chain": "/api/evidence/{id}/chain - Chain of custody",
            "tod": "/api/cases/{id}/tod - Time of death calculator",
            "decomposition": "/api/cases/{id}/decomposition - Decomposition logs",
            "missing": "/api/missing-persons - Missing person reports",
            "matching": "/api/cases/{id}/find-matches - Body matching",
            "alerts": "/api/alerts - Pattern alerts",
            "search": "/api/search - Advanced search",
            "stats": "/api/search/stats - Statistics"
        }
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

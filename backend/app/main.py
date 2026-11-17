from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.routes import datasets, jobs, research
from backend.database.session import init_db

# Initialize database schema on startup
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Genomic & Multi-Omics Analysis Platform API Engine"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Multi-Tenant Isolation & Audit Middleware
@app.middleware("http")
async def tenant_isolation_middleware(request: Request, call_next):
    # Ensure tenant header exists or inject default
    tenant_id = request.headers.get("X-Tenant-ID", settings.DEFAULT_TENANT_ID)
    request.state.tenant_id = tenant_id

    response: Response = await call_next(request)
    response.headers["X-Tenant-ID"] = tenant_id
    return response

# Routes
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(research.router, prefix="/api/v1")

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "platform": "GISAP",
        "version": settings.VERSION,
        "default_tenant": settings.DEFAULT_TENANT_ID
    }

@app.get("/metrics", tags=["Observability"])
def prometheus_metrics():
    """
    Exposes metrics in standard Prometheus text format.
    """
    lines = [
        "# HELP gisap_system_status Operational status of GISAP platform",
        "# TYPE gisap_system_status gauge",
        "gisap_system_status{tier=\"alpha\"} 1",
        "# HELP gisap_api_requests_total Total HTTP requests handled",
        "# TYPE gisap_api_requests_total counter",
        "gisap_api_requests_total{handler=\"api_v1\"} 42",
    ]
    return Response(content="\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Modeller SQLAlchemy relationship registry içinde
# eksiksiz yüklensin diye import ediliyor.
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.team import Team
from app.models.user import User

from app.routers.auth_router import router as auth_router
from app.routers.company_router import router as company_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.department_router import router as department_router
from app.routers.employee_router import router as employee_router
from app.routers.leave_router import router as leave_router
from app.routers.platform_router import router as platform_router
from app.routers.team_router import router as team_router


app = FastAPI(
    title="HR Management API",
    description="Multi-tenant Human Resources Management Platform",
    version="2.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

allowed_origins = [
    # Angular local development
    "http://localhost:4200",
    "http://127.0.0.1:4200",

    # Capacitor Android
    "http://localhost",
    "https://localhost",

    # Vercel production
    "https://hr-management-system-lilac.vercel.app",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,

    # Vercel preview / deployment adresleri
    allow_origin_regex=r"^https://.*\.vercel\.app$",

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

# Authentication
app.include_router(auth_router)

# Platform owner işlemleri
app.include_router(platform_router)

# Company & organization
app.include_router(company_router)
app.include_router(department_router)
app.include_router(team_router)

# Human Resources
app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(dashboard_router)


# ============================================================
# SYSTEM ENDPOINTS
# ============================================================

@app.get("/", tags=["System"])
def home():
    return {
        "message": "HR Management API is running.",
        "version": "2.0.0",
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
    }


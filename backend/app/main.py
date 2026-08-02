from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

# SQLAlchemy tablo oluşturma sırasında bütün modelleri görsün.
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.team import Team
from app.models.user import User

from app.routers.auth_router import (
    router as auth_router,
)
from app.routers.company_router import (
    router as company_router,
)
from app.routers.dashboard_router import (
    router as dashboard_router,
)
from app.routers.department_router import (
    router as department_router,
)
from app.routers.employee_router import (
    router as employee_router,
)
from app.routers.leave_router import (
    router as leave_router,
)
from app.routers.team_router import (
    router as team_router,
)


# Import edilen modeller için eksik tabloları oluşturur.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="HR Management API",
    description="Human Resources Leave Management System",
    version="1.0.0",
)


allowed_origins = [
    # Yerel Angular
    "http://localhost:4200",
    "http://127.0.0.1:4200",

    # Vercel production domain
    "https://hr-management-system-lilac.vercel.app",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,

    # Vercel'in her deploy sırasında ürettiği preview adresleri
    allow_origin_regex=(
        r"^https://hr-management-system-"
        r"[a-zA-Z0-9-]+-dursuns-projects-630978bb"
        r"\.vercel\.app$"
    ),

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Authentication
app.include_router(auth_router)

# Organization structure
app.include_router(company_router)
app.include_router(department_router)
app.include_router(team_router)

# Human resources
app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(dashboard_router)


@app.get(
    "/",
    tags=["System"],
)
def home():
    return {
        "message": "HR Management API is running."
    }


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {
        "status": "healthy"
    }
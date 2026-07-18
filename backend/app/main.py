from app.create_admin import create_initial_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

from app.models.user import User
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest

from app.routers.auth_router import router as auth_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.employee_router import router as employee_router
from app.routers.leave_router import router as leave_router


Base.metadata.create_all(bind=engine)
create_initial_admin()

app = FastAPI(
    title="HR Management API",
    description="Human Resources Leave Management System",
    version="1.0.0",
)


allowed_origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",

    "https://hr-management-system-lilac.vercel.app",
]


app.add_middleware(
    CORSMiddleware,

    # Sabit adresler
    allow_origins=allowed_origins,

    allow_origin_regex=(
        r"^https://hr-management-system-"
        r"[a-zA-Z0-9-]+-dursuns-projects-630978bb\.vercel\.app$"
    ),

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(dashboard_router)


@app.get("/", tags=["System"])
def home():
    return {
        "message": "HR Management API is running."
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy"
    }
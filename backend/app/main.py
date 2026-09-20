from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import Base, engine, SessionLocal, get_db

from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.team import Team
from app.models.user import User
from app.models.quiz_and_shift import Quiz, QuizSubmission, ShiftSchedule

from app.security.password import hash_password
from app.security.user_role import UserRole

from app.routers.auth_router import router as auth_router
from app.routers.company_router import router as company_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.department_router import router as department_router
from app.routers.employee_router import router as employee_router
from app.routers.leave_router import router as leave_router
from app.routers.platform_router import router as platform_router
from app.routers.team_router import router as team_router
from app.routers.quiz_shift_router import router as quiz_shift_router


def init_db():
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("DROP TABLE IF EXISTS teams CASCADE;"))
    except Exception as e:
        print(f"Tablo temizleme notu: {e}")

    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # 0. Varsayilan Sirket Guvencesi
        company = db.query(Company).first()
        if not company:
            company = Company(
                name="Muslu Teknoloji A.S.",
                subdomain="muslu",
                is_active=True
            )
            db.add(company)
            db.commit()
            db.refresh(company)

        # 1. Platform Owner (dursun)
        owner = db.query(User).filter(User.username == "dursun").first()
        if owner:
            owner.password = hash_password("123456")
            owner.role = UserRole.PLATFORM_OWNER.value
            owner.is_active = True
            owner.must_change_password = False
            owner.company_id = None
        else:
            owner = User(
                username="dursun",
                password=hash_password("123456"),
                role=UserRole.PLATFORM_OWNER.value,
                is_active=True,
                must_change_password=False,
                company_id=None,
            )
            db.add(owner)

        # 2. Sirket Yoneticisi (dmuslu)
        manager = db.query(User).filter(User.username == "dmuslu").first()
        if manager:
            manager.password = hash_password("123456")
            manager.role = UserRole.YONETICI.value
            manager.is_active = True
            manager.must_change_password = False
            manager.company_id = company.id
        else:
            manager = User(
                username="dmuslu",
                password=hash_password("123456"),
                role=UserRole.YONETICI.value,
                is_active=True,
                must_change_password=False,
                company_id=company.id,
            )
            db.add(manager)

        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"ERROR initializing database: {exc}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="HR Management API",
    description="Multi-tenant Human Resources Management Platform",
    version="2.0.0",
    lifespan=lifespan,
)

# ============================================================
# CORS CONFIGURATION
# ============================================================

allowed_origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost",
    "https://localhost",
    "https://hr-management-system-lilac.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(platform_router)
app.include_router(company_router)
app.include_router(department_router)
app.include_router(team_router)
app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(dashboard_router)
app.include_router(quiz_shift_router)


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


@app.get("/seed-fast", tags=["Seed"])
def run_seed_fast(db: Session = Depends(get_db)):
    try:
        # 1. Sirket
        comp = db.query(Company).first()
        if not comp:
            comp = Company(name="Muslu Teknoloji A.S.", subdomain="muslu", is_active=True)
            db.add(comp)
            db.commit()
            db.refresh(comp)

        # 2. Departman
        dept = db.query(Department).filter_by(company_id=comp.id, name="Yazilim & Bilisim").first()
        if not dept:
            dept = Department(company_id=comp.id, name="Yazilim & Bilisim")
            db.add(dept)
            db.commit()
            db.refresh(dept)

        # 3. Takim
        team = db.query(Team).filter_by(name="Frontend & Mobil Ekibi").first()
        if not team:
            team = Team(department_id=dept.id, name="Frontend & Mobil Ekibi")
            db.add(team)
            db.commit()
            db.refresh(team)

        # 4. Takim Lideri (lider.ahmet)
        lead_user = db.query(User).filter_by(username="lider.ahmet").first()
        if not lead_user:
            lead_user = User(
                username="lider.ahmet",
                password=hash_password("123456"),
                role=UserRole.TAKIM_LIDERI.value,
                company_id=comp.id,
                is_active=True,
                must_change_password=False,
            )
            db.add(lead_user)
            db.commit()
            db.refresh(lead_user)

        lead_emp = db.query(Employee).filter_by(user_id=lead_user.id).first()
        if not lead_emp:
            lead_emp = Employee(
                user_id=lead_user.id,
                team_id=team.id,
                first_name="Ahmet",
                last_name="Lider",
                tc_no="10000000001",
                employee_number="TL001",
                department="Yazilim & Bilisim",
                position="Takim Lideri",
                phone="05551112233",
                email="lider.ahmet@muslu.com",
                hire_date=date(2025, 1, 1),
                remaining_annual_leave=14,
            )
            db.add(lead_emp)
            db.commit()
            db.refresh(lead_emp)

            team.team_leader_id = lead_emp.id
            db.commit()

        # 5. Personel (mehmet.oz)
        user_p = db.query(User).filter_by(username="mehmet.oz").first()
        if not user_p:
            user_p = User(
                username="mehmet.oz",
                password=hash_password("123456"),
                role=UserRole.PERSONEL.value,
                company_id=comp.id,
                is_active=True,
                must_change_password=False,
            )
            db.add(user_p)
            db.commit()
            db.refresh(user_p)

        emp_p = db.query(Employee).filter_by(user_id=user_p.id).first()
        if not emp_p:
            emp_p = Employee(
                user_id=user_p.id,
                team_id=team.id,
                first_name="Mehmet",
                last_name="Oz",
                tc_no="10000000002",
                employee_number="P002",
                department="Yazilim & Bilisim",
                position="Full Stack Dev",
                phone="05551112234",
                email="mehmet.oz@muslu.com",
                hire_date=date(2025, 2, 1),
                remaining_annual_leave=14,
            )
            db.add(emp_p)
            db.commit()

        # 6. Sinav (Quiz)
        if not db.query(Quiz).filter_by(company_id=comp.id).first():
            db.add(Quiz(
                company_id=comp.id,
                title="Temel ISG ve Bilgi Guvenligi",
                description="Tum ekipler icin zorunlu yeterlilik sinavi.",
                duration_minutes=10,
                is_active=True,
                questions=[
                    {
                        "text": "Acil cikis kapilari mesai saatinde nasil tutulmalidir?",
                        "options": ["Kilitli", "Her zaman acik ve engelsiz", "Yalnizca anahtarla acilabilir"],
                        "correct_index": 1
                    },
                    {
                        "text": "Masa basinda temiz ekran kurali neyi ifade eder?",
                        "options": ["Monitorun tozunu almayi", "Bilgisayar basindan ayrilirken ekrani kilitlemeyi (Win+L)", "Ekran koruyucu acmayi"],
                        "correct_index": 1
                    }
                ]
            ))
            db.commit()

        # 7. Vardiya (ShiftSchedule)
        today = date.today().isoformat()
        if not db.query(ShiftSchedule).filter_by(company_id=comp.id, shift_date=today, employee_id=None).first():
            db.add(ShiftSchedule(
                company_id=comp.id,
                shift_date=today,
                start_time="09:00",
                end_time="18:00",
                break_1="10:30 - 10:45",
                lunch_break="12:30 - 13:00",
                break_2="15:00 - 15:15",
                break_3="16:45 - 17:00"
            ))
            db.commit()

        return {"status": "success", "message": "Sirket, Takim Lideri, Personel ve Quiz seed islemi tamamlandi!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Seed Hatasi: {str(e)}")
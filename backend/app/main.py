from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database.database import Base, engine, SessionLocal

# Modeller SQLAlchemy relationship registry içinde
# eksiksiz yüklensin diye import ediliyor.
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
    # 1. Tabloları PostgreSQL üzerinde oluştur
    Base.metadata.create_all(bind=engine)

    # 2. Kullanıcıları garantile ve şifrelerini senkronize et
    db: Session = SessionLocal()
    try:
        # Platform Owner (dursun)
        owner = db.query(User).filter(User.username == "dursun").first()
        if owner:
            owner.password = hash_password("123456")
            owner.role = UserRole.PLATFORM_OWNER.value
            owner.is_active = True
            owner.must_change_password = False
            owner.company_id = None
            print("INFO: Platform owner 'dursun' password successfully synced to 123456.")
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
            print("INFO: Platform owner 'dursun' created with password 123456.")

        # Şirket Yöneticisi (dmuslu)
        manager = db.query(User).filter(User.username == "dmuslu").first()
        if manager:
            manager.password = hash_password("123456")
            manager.role = UserRole.YONETICI.value
            manager.is_active = True
            manager.must_change_password = False
            if not manager.company_id:
                first_company = db.query(Company).first()
                if first_company:
                    manager.company_id = first_company.id
            print("INFO: Manager 'dmuslu' password set to 123456.")

        # Test yöneticisi (mehmet)
        manager_mehmet = db.query(User).filter(User.username == "mehmet").first()
        if manager_mehmet:
            manager_mehmet.password = hash_password("123456")
            manager_mehmet.role = UserRole.YONETICI.value
            manager_mehmet.is_active = True
            manager_mehmet.must_change_password = False
            if not manager_mehmet.company_id:
                first_company = db.query(Company).first()
                if first_company:
                    manager_mehmet.company_id = first_company.id

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

# Quiz & Shift Operations
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
    from app.models.company import Company
    from app.models.department import Department
    from app.models.employee import Employee
    from app.models.user import User
    from app.models.quiz_and_shift import Quiz, ShiftSchedule
    from app.security.password import hash_password
    from app.security.user_role import UserRole
    from datetime import date

    comp = db.query(Company).first()
    if not comp:
        return {"status": "error", "message": "Sistemde şirket bulunamadı!"}

    # 1. Departmanlar
    dept_map = {}
    for d_name, d_code in [("Yazılım & Bilişim", "YAZ"), ("İnsan Kaynakları", "IK"), ("Pazarlama & Satış", "PAZ")]:
        dept = db.query(Department).filter_by(company_id=comp.id, name=d_name).first()
        if not dept:
            dept = Department(company_id=comp.id, name=d_name, code=d_code)
            db.add(dept)
            db.flush()
        dept_map[d_name] = dept.id

    # 2. Hazır Personeller
    demo_users = [
        {"u": "ahmet.yilmaz", "name": "Ahmet", "last": "Yılmaz", "title": "Frontend Dev", "dept": dept_map["Yazılım & Bilişim"]},
        {"u": "ayse.kaya", "name": "Ayşe", "last": "Kaya", "title": "İK Uzmanı", "dept": dept_map["İnsan Kaynakları"]},
        {"u": "mehmet.oz", "name": "Mehmet", "last": "Öz", "title": "Full Stack Dev", "dept": dept_map["Yazılım & Bilişim"]},
    ]

    for p in demo_users:
        if not db.query(User).filter_by(username=p["u"]).first():
            user = User(
                username=p["u"],
                password=hash_password("123456"),
                role=UserRole.PERSONEL.value,
                company_id=comp.id,
                is_active=True,
                must_change_password=False
            )
            db.add(user)
            db.flush()

            emp = Employee(
                company_id=comp.id,
                user_id=user.id,
                department_id=p["dept"],
                first_name=p["name"],
                last_name=p["last"],
                job_title=p["title"],
                hire_date=date(2025, 1, 15),
                work_email=f"{p['u']}@sirket.com",
                annual_leave_balance=14
            )
            db.add(emp)

    # 3. Quiz
    if not db.query(Quiz).filter_by(company_id=comp.id).first():
        db.add(Quiz(
            company_id=comp.id,
            title="İş Sağlığı ve Güvenliği (İSG) Sınavı",
            description="Temel zorunlu eğitim değerlendirmesi.",
            duration_minutes=10,
            is_active=True,
            questions=[
                {
                    "text": "Acil durumda tahliye toplanma alanına nasıl gidilir?",
                    "options": ["Asansör kullanarak", "Yangın merdiveni ve acil çıkış levhalarını izleyerek", "Koşarak"],
                    "correct_index": 1
                },
                {
                    "text": "Bilgisayar başında 20-20-20 kuralı neyi ifade eder?",
                    "options": ["20 dakikada bir 20 saniye 6 metre uzağa bakmayı", "20 saat çalışmayı", "Hiç mola vermemeyi"],
                    "correct_index": 0
                }
            ]
        ))

    # 4. Vardiya
    today = date.today().isoformat()
    if not db.query(ShiftSchedule).filter_by(company_id=comp.id, shift_date=today).first():
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
    return {"status": "success", "message": "Demo personeller, sınavlar ve vardiya başarıyla veritabanına işlendi!"}

from datetime import date
from io import BytesIO
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import pandas as pd
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.team import Team
from app.models.user import User
from app.models.quiz_and_shift import ShiftSchedule
from app.security.auth_dependency import require_manager_or_owner
from app.security.password import hash_password
from app.security.user_role import UserRole

router = APIRouter(prefix="/bulk", tags=["Bulk Operations"])


@router.post("/upload-employees")
async def upload_employees_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_owner),
):
    """
    Excel üzerinden toplu personel, departman, takım ve kullanıcı oluşturur.
    Takım lideri belirtilmişse takıma lider olarak bağlar.
    """
    try:
        content = await file.read()
        # xlsx veya csv desteği
        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(content), dtype=str)
        else:
            # Personel_Ve_Takimlar sayfası varsa onu oku, yoksa ilk sayfayı al
            xls = pd.ExcelFile(BytesIO(content))
            sheet = "Personel_Ve_Takimlar" if "Personel_Ve_Takimlar" in xls.sheet_names else 0
            df = pd.read_excel(xls, sheet_name=sheet, dtype=str)

        company_id = current_user.company_id or 1
        created_count = 0

        for _, row in df.iterrows():
            tc = str(row.get("tc_no", "")).strip()
            email = str(row.get("email", "")).strip()
            if not tc or not email or tc.lower() == "nan":
                continue

            first_name = str(row.get("first_name", "")).strip()
            last_name = str(row.get("last_name", "")).strip()
            dept_name = str(row.get("department", "Genel")).strip()
            team_name = str(row.get("team_name", "Varsayılan Takım")).strip()
            team_leader_name = str(row.get("team_leader_name", "")).strip()
            role_str = str(row.get("role", "PERSONEL")).strip().upper()
            position = str(row.get("position", "Personel")).strip()
            phone = str(row.get("phone", "")).strip()

            # 1. Departman bul veya oluştur
            dept = db.query(Department).filter_by(company_id=company_id, name=dept_name).first()
            if not dept:
                dept = Department(company_id=company_id, name=dept_name)
                db.add(dept)
                db.commit()
                db.refresh(dept)

            # 2. Takım bul veya oluştur
            team = db.query(Team).filter_by(department_id=dept.id, name=team_name).first()
            if not team:
                team = Team(department_id=dept.id, name=team_name)
                db.add(team)
                db.commit()
                db.refresh(team)

            # 3. Kullanıcı hesabı aç
            username = email.split("@")[0]
            user = db.query(User).filter_by(username=username).first()
            if not user:
                assigned_role = UserRole.TAKIM_LIDERI.value if role_str == "TAKIM_LIDERI" else UserRole.PERSONEL.value
                user = User(
                    username=username,
                    password=hash_password("123456"),
                    role=assigned_role,
                    company_id=company_id,
                    is_active=True,
                    must_change_password=False,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # 4. Employee kartını oluştur
            emp = db.query(Employee).filter_by(user_id=user.id).first()
            if not emp:
                emp = Employee(
                    user_id=user.id,
                    team_id=team.id,
                    first_name=first_name,
                    last_name=last_name,
                    tc_no=tc,
                    employee_number=f"EMP{user.id:03d}",
                    department=dept_name,
                    position=position,
                    phone=phone,
                    email=email,
                    hire_date=date.today(),
                    remaining_annual_leave=14,
                )
                db.add(emp)
                db.commit()
                db.refresh(emp)
                created_count += 1

            # 5. Takım Lideri Ataması (Dursun Muslu veya satırdaki lider)
            if "Dursun" in team_leader_name or "dmuslu" in team_leader_name:
                mgr = db.query(User).filter_by(username="dmuslu").first()
                if mgr and mgr.employee_profile:
                    team.team_leader_id = mgr.employee_profile.id
            elif role_str == "TAKIM_LIDERI":
                team.team_leader_id = emp.id

            db.commit()

        return {
            "status": "success",
            "message": f"{created_count} personel başarıyla oluşturuldu ve takımlara atandı."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Excel personel yükleme hatası: {str(e)}")


@router.post("/upload-shifts")
async def upload_shifts_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_owner),
):
    """
    Excel üzerinden günlük vardiya ve mola saatlerini günceller.
    """
    try:
        content = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(content), dtype=str)
        else:
            xls = pd.ExcelFile(BytesIO(content))
            sheet = "Gunluk_Vardiya_Cizelgesi" if "Gunluk_Vardiya_Cizelgesi" in xls.sheet_names else 0
            df = pd.read_excel(xls, sheet_name=sheet, dtype=str)

        updated_count = 0
        company_id = current_user.company_id or 1

        for _, row in df.iterrows():
            tc = str(row.get("tc_no", "")).strip()
            shift_date = str(row.get("shift_date", "")).strip()
            if not tc or not shift_date or tc.lower() == "nan":
                continue

            emp = db.query(Employee).filter(Employee.tc_no == tc).first()
            if not emp:
                continue

            shift = db.query(ShiftSchedule).filter(
                ShiftSchedule.company_id == company_id,
                ShiftSchedule.shift_date == shift_date,
                ShiftSchedule.employee_id == emp.id
            ).first()

            if not shift:
                shift = ShiftSchedule(
                    company_id=company_id,
                    employee_id=emp.id,
                    shift_date=shift_date
                )
                db.add(shift)

            shift.start_time = str(row.get("start_time", "09:00"))
            shift.end_time = str(row.get("end_time", "18:00"))
            shift.break_1 = str(row.get("break_1", "-"))
            shift.lunch_break = str(row.get("lunch_break", "-"))
            shift.break_2 = str(row.get("break_2", "-"))
            shift.break_3 = str(row.get("break_3", "-"))
            updated_count += 1

        db.commit()
        return {
            "status": "success",
            "message": f"{updated_count} personelin günlük vardiya ve mola verisi güncellendi."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Vardiya Excel yükleme hatası: {str(e)}")
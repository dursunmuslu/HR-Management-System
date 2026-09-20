from datetime import date
from io import BytesIO
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import pandas as pd
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.department import Department
from app.models.employee import Employee
from app.models.team import Team
from app.models.user import User
from app.security.auth_dependency import require_manager_or_owner
from app.security.password import hash_password
from app.security.user_role import UserRole

router = APIRouter(prefix="/bulk", tags=["Bulk Operations"])


@router.post("/upload-employees")
async def upload_employees_excel(
    file: UploadFile = File(...),
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_owner),
):
    try:
        content = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(content), dtype=str)
        else:
            xls = pd.ExcelFile(BytesIO(content))
            sheet = "Personel_Ve_Takimlar" if "Personel_Ve_Takimlar" in xls.sheet_names else 0
            df = pd.read_excel(xls, sheet_name=sheet, dtype=str)

        target_company_id = current_user.company_id
        if current_user.role == UserRole.PLATFORM_OWNER.value:
            target_company_id = company_id or current_user.company_id or 1

        if not target_company_id:
            raise HTTPException(status_code=400, detail="Hedef şirket belirlenemedi.")

        created_count = 0
        updated_count = 0
        leader_assignments = []

        for _, row in df.iterrows():
            tc = str(row.get("tc_no", "")).strip()
            email = str(row.get("email", "")).strip().lower()
            if not tc or not email or tc.lower() == "nan" or email.lower() == "nan":
                continue

            first_name = str(row.get("first_name", "")).strip()
            last_name = str(row.get("last_name", "")).strip()
            dept_name = str(row.get("department", "Genel")).strip()
            team_name = str(row.get("team_name", "Genel Ekip")).strip()
            role_str = str(row.get("role", "PERSONEL")).strip().upper()
            position = str(row.get("position", "Personel")).strip()
            phone = str(row.get("phone", "")).strip()

            # 1. Departman
            dept = db.query(Department).filter_by(company_id=target_company_id, name=dept_name).first()
            if not dept:
                dept = Department(company_id=target_company_id, name=dept_name)
                db.add(dept)
                db.commit()
                db.refresh(dept)

            # 2. Takım
            team = db.query(Team).filter_by(department_id=dept.id, name=team_name).first()
            if not team:
                team = Team(department_id=dept.id, name=team_name)
                db.add(team)
                db.commit()
                db.refresh(team)

            # 3. User Hesabı (Sadece username üzerinden kontrol edilir, User modelinde email yoktur)
            username = email.split("@")[0]
            user = db.query(User).filter(User.username == username).first()
            assigned_role = UserRole.TAKIM_LIDERI.value if "LIDER" in role_str else UserRole.PERSONEL.value

            if not user:
                user = User(
                    username=username,
                    password=hash_password("123456"),
                    role=assigned_role,
                    company_id=target_company_id,
                    is_active=True,
                    must_change_password=False,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                user.role = assigned_role
                user.company_id = target_company_id
                db.commit()

            # 4. Employee Kartı Kontrolü (TC veya Email Employee tablosundan kontrol edilir)
            emp = db.query(Employee).filter(
                (Employee.tc_no == tc) | (Employee.email == email) | (Employee.user_id == user.id)
            ).first()

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
            else:
                emp.first_name = first_name or emp.first_name
                emp.last_name = last_name or emp.last_name
                emp.team_id = team.id
                emp.department = dept_name
                emp.position = position
                emp.phone = phone
                emp.email = email
                db.commit()
                updated_count += 1

            if assigned_role == UserRole.TAKIM_LIDERI.value:
                leader_assignments.append((team.id, emp.id))

        # 5. Takım Liderlerini Takımlara Bağla
        for t_id, leader_emp_id in leader_assignments:
            t = db.query(Team).filter(Team.id == t_id).first()
            if t:
                t.team_leader_id = leader_emp_id
                db.commit()

        return {
            "status": "success",
            "message": f"{created_count} personel eklendi, {updated_count} personel güncellendi.",
            "created": created_count,
            "updated": updated_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Excel aktarım hatası: {str(e)}")
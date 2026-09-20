from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import pandas as pd
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.attendance_timesheet import AttendanceTimesheet, PerformanceSurveyScore
from app.models.employee import Employee
from app.models.team import Team
from app.models.user import User
from app.security.auth_dependency import get_current_user, require_company_user
from app.security.user_role import UserRole

router = APIRouter(prefix="/timesheets", tags=["Puantaj ve Performans"])


@router.get("/my-records")
def get_my_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_user),
):
    """Personelin kendi süre ve anket puanlarını getirdiği uç nokta"""
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        return {"timesheets": [], "surveys": []}

    timesheets = (
        db.query(AttendanceTimesheet)
        .filter(AttendanceTimesheet.employee_id == emp.id)
        .order_by(AttendanceTimesheet.work_date.desc())
        .all()
    )

    surveys = (
        db.query(PerformanceSurveyScore)
        .filter(PerformanceSurveyScore.employee_id == emp.id)
        .order_by(PerformanceSurveyScore.period_month.desc())
        .all()
    )

    return {
        "timesheets": [
            {
                "id": t.id,
                "work_date": str(t.work_date),
                "expected_minutes": t.expected_minutes,
                "actual_minutes": t.actual_minutes,
                "diff_minutes": t.diff_minutes,
                "description": t.description or "",
            }
            for t in timesheets
        ],
        "surveys": [
            {
                "id": s.id,
                "period_month": s.period_month,
                "survey_type": s.survey_type,
                "target_score": s.target_score,
                "actual_score": s.actual_score,
                "survey_count": s.survey_count,
                "feedback_note": s.feedback_note or "",
            }
            for s in surveys
        ],
    }


@router.get("/company-records")
def get_company_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Yönetici ve Takım Liderinin tüm veya takım kayıtlarını getirdiği uç nokta"""
    query_ts = db.query(AttendanceTimesheet).join(Employee, Employee.id == AttendanceTimesheet.employee_id)
    query_sv = db.query(PerformanceSurveyScore).join(Employee, Employee.id == PerformanceSurveyScore.employee_id)

    if current_user.role in [UserRole.YONETICI.value, UserRole.PLATFORM_OWNER.value]:
        query_ts = query_ts.filter(AttendanceTimesheet.company_id == current_user.company_id)
        query_sv = query_sv.filter(PerformanceSurveyScore.company_id == current_user.company_id)
    elif current_user.role == UserRole.TAKIM_LIDERI.value:
        leader_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not leader_emp:
            return {"timesheets": [], "surveys": []}
        team_ids = [t.id for t in db.query(Team).filter(Team.team_leader_id == leader_emp.id).all()]
        query_ts = query_ts.filter(Employee.team_id.in_(team_ids))
        query_sv = query_sv.filter(Employee.team_id.in_(team_ids))
    else:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim.")

    ts_list = query_ts.order_by(AttendanceTimesheet.work_date.desc()).all()
    sv_list = query_sv.order_by(PerformanceSurveyScore.period_month.desc()).all()

    return {
        "timesheets": [
            {
                "id": t.id,
                "employee_id": t.employee_id,
                "full_name": f"{t.employee.first_name} {t.employee.last_name}",
                "tc_no": t.employee.tc_no,
                "work_date": str(t.work_date),
                "expected_minutes": t.expected_minutes,
                "actual_minutes": t.actual_minutes,
                "diff_minutes": t.diff_minutes,
                "description": t.description or "",
            }
            for t in ts_list
        ],
        "surveys": [
            {
                "id": s.id,
                "employee_id": s.employee_id,
                "full_name": f"{s.employee.first_name} {s.employee.last_name}",
                "tc_no": s.employee.tc_no,
                "period_month": s.period_month,
                "survey_type": s.survey_type,
                "target_score": s.target_score,
                "actual_score": s.actual_score,
                "survey_count": s.survey_count,
                "feedback_note": s.feedback_note or "",
            }
            for s in sv_list
        ],
    }


@router.post("/upload")
async def upload_timesheets_and_surveys(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Excel içindeki Login_Sureleri ve Anket_Ve_Performans_Puanlari sayfalarını okur"""
    if current_user.role not in [UserRole.YONETICI.value, UserRole.PLATFORM_OWNER.value, UserRole.TAKIM_LIDERI.value]:
        raise HTTPException(status_code=403, detail="Yalnızca yönetici ve takım liderleri yükleme yapabilir.")

    try:
        content = await file.read()
        xls = pd.ExcelFile(BytesIO(content))

        ts_count = 0
        sv_count = 0

        # 1. Login Süreleri Sayfası
        if "Login_Sureleri" in xls.sheet_names:
            df_ts = pd.read_excel(xls, sheet_name="Login_Sureleri", dtype=str)
            for _, row in df_ts.iterrows():
                tc = str(row.get("tc_no", "")).strip()
                w_date_str = str(row.get("work_date", "")).strip()
                if not tc or not w_date_str or tc == "nan":
                    continue

                emp = db.query(Employee).filter(Employee.tc_no == tc).first()
                if not emp:
                    continue

                work_date = datetime.strptime(w_date_str[:10], "%Y-%m-%d").date()
                expected = int(row.get("expected_minutes", 540))
                actual = int(row.get("actual_minutes", 0))
                diff = int(row.get("diff_minutes", actual - expected))
                desc = str(row.get("description", "")).strip()
                if desc == "nan":
                    desc = ""

                record = (
                    db.query(AttendanceTimesheet)
                    .filter(AttendanceTimesheet.employee_id == emp.id, AttendanceTimesheet.work_date == work_date)
                    .first()
                )
                if record:
                    record.expected_minutes = expected
                    record.actual_minutes = actual
                    record.diff_minutes = diff
                    record.description = desc
                else:
                    record = AttendanceTimesheet(
                        company_id=current_user.company_id,
                        employee_id=emp.id,
                        work_date=work_date,
                        expected_minutes=expected,
                        actual_minutes=actual,
                        diff_minutes=diff,
                        description=desc,
                    )
                    db.add(record)
                ts_count += 1

        # 2. Anket ve Performans Puanları Sayfası
        if "Anket_Ve_Performans_Puanlari" in xls.sheet_names:
            df_sv = pd.read_excel(xls, sheet_name="Anket_Ve_Performans_Puanlari", dtype=str)
            for _, row in df_sv.iterrows():
                tc = str(row.get("tc_no", "")).strip()
                period = str(row.get("period_month", "")).strip()
                stype = str(row.get("survey_type", "Müşteri Memnuniyeti (CSAT)")).strip()
                if not tc or not period or tc == "nan":
                    continue

                emp = db.query(Employee).filter(Employee.tc_no == tc).first()
                if not emp:
                    continue

                target = float(row.get("target_score", 85.0))
                actual = float(row.get("actual_score", 0.0))
                count = int(row.get("survey_count", 1))
                feedback = str(row.get("feedback_note", "")).strip()
                if feedback == "nan":
                    feedback = ""

                sv_record = (
                    db.query(PerformanceSurveyScore)
                    .filter(
                        PerformanceSurveyScore.employee_id == emp.id,
                        PerformanceSurveyScore.period_month == period,
                        PerformanceSurveyScore.survey_type == stype,
                    )
                    .first()
                )
                if sv_record:
                    sv_record.target_score = target
                    sv_record.actual_score = actual
                    sv_record.survey_count = count
                    sv_record.feedback_note = feedback
                else:
                    sv_record = PerformanceSurveyScore(
                        company_id=current_user.company_id,
                        employee_id=emp.id,
                        period_month=period,
                        survey_type=stype,
                        target_score=target,
                        actual_score=actual,
                        survey_count=count,
                        feedback_note=feedback,
                    )
                    db.add(sv_record)
                sv_count += 1

        db.commit()
        return {
            "status": "success",
            "message": f"Aktarım tamamlandı! {ts_count} login süresi ve {sv_count} anket puanı işlendi.",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"İçe aktarma hatası: {str(e)}")
from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.company import Company
from app.models.quiz_and_shift import Quiz, QuizSubmission, ShiftSchedule
from app.models.user import User
from app.models.employee import Employee
from app.models.team import Team
from app.security.auth_dependency import (
    get_current_user,
    require_leader_manager_or_owner,
)
from app.security.user_role import UserRole

router = APIRouter(prefix="/operations", tags=["Quiz and Shifts"])


class QuizCreateSchema(BaseModel):
    title: str
    description: Optional[str] = ""
    duration_minutes: int = 15
    questions: list


class QuizSubmitSchema(BaseModel):
    selected_answers: List[int]


class ShiftSaveSchema(BaseModel):
    shift_date: Optional[str] = None
    employee_id: Optional[int] = None
    start_time: str = "09:00"
    end_time: str = "18:00"
    break_1: str = "10:30 - 10:45"
    lunch_break: str = "12:30 - 13:00"
    break_2: str = "15:00 - 15:15"
    break_3: str = "16:45 - 17:00"


# ================= QUIZ ENDPOINTS =================

@router.post("/quizzes")
def create_quiz(
    data: QuizCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_manager_or_owner),
):
    target_company_id = current_user.company_id

    if current_user.role == UserRole.PLATFORM_OWNER.value and not target_company_id:
        first_comp = db.query(Company).first()
        target_company_id = first_comp.id if first_comp else 1

    if not target_company_id:
        raise HTTPException(status_code=400, detail="Hesabınız bir şirkete bağlı değil.")

    quiz = Quiz(
        company_id=target_company_id,
        title=data.title,
        description=data.description or "",
        duration_minutes=data.duration_minutes,
        questions=data.questions,
        is_active=True,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("/quizzes")
def list_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Quiz).filter(Quiz.is_active.is_(True))
    if current_user.company_id:
        query = query.filter(Quiz.company_id == current_user.company_id)

    quizzes = query.all()
    submissions = {
        s.quiz_id: s
        for s in db.query(QuizSubmission).filter(QuizSubmission.user_id == current_user.id).all()
    }

    privileged_roles = [
        UserRole.YONETICI.value,
        UserRole.PLATFORM_OWNER.value,
        UserRole.TAKIM_LIDERI.value,
    ]

    result = []
    for q in quizzes:
        sub = submissions.get(q.id)
        safe_questions = []
        for ques in (q.questions or []):
            item: Dict[str, Any] = {
                "text": ques.get("text"),
                "options": ques.get("options", []),
            }
            if current_user.role in privileged_roles:
                item["correct_index"] = ques.get("correct_index")
            safe_questions.append(item)

        result.append(
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "duration_minutes": q.duration_minutes,
                "total_questions": len(q.questions or []),
                "questions": safe_questions,
                "is_completed": sub is not None,
                "score": sub.score if sub else None,
                "completed_at": sub.completed_at if sub else None,
            }
        )
    return result


@router.get("/quizzes/{quiz_id}/submissions")
def get_quiz_submissions(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_manager_or_owner),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz bulunamadı.")

    if current_user.role != UserRole.PLATFORM_OWNER.value:
        if quiz.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Bu quize erişim yetkiniz yok.")

    submissions = (
        db.query(QuizSubmission)
        .filter(QuizSubmission.quiz_id == quiz_id)
        .order_by(QuizSubmission.id.desc())
        .all()
    )

    leader_team_id = None
    if current_user.role == UserRole.TAKIM_LIDERI.value:
        leader_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        leader_team_id = leader_emp.team_id if leader_emp else None

    user_ids = [s.user_id for s in submissions]
    employees = db.query(Employee).filter(Employee.user_id.in_(user_ids)).all() if user_ids else []
    emp_by_user = {e.user_id: e for e in employees}

    team_ids = [e.team_id for e in employees if e.team_id]
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all() if team_ids else []
    team_by_id = {t.id: t.name for t in teams}

    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_by_id = {u.id: u for u in users}

    results = []
    for sub in submissions:
        emp = emp_by_user.get(sub.user_id)
        usr = user_by_id.get(sub.user_id)

        if leader_team_id is not None:
            if not emp or emp.team_id != leader_team_id:
                continue

        if emp:
            emp_name = f"{emp.first_name} {emp.last_name}"
            job_title = getattr(emp, "position", None) or getattr(emp, "job_title", "Personel")
            team_name = team_by_id.get(emp.team_id, "Genel Ekip")
        elif usr:
            emp_name = usr.username
            job_title = "Kullanıcı"
            team_name = "Takımsız"
        else:
            emp_name = "Bilinmeyen Kullanıcı"
            job_title = "-"
            team_name = "-"

        total = sub.total_questions if (sub.total_questions and sub.total_questions > 0) else len(quiz.questions or [])
        percentage = round((sub.score / total) * 100, 1) if total > 0 else 0

        submitted_date = "Tamamlandı"
        if getattr(sub, "completed_at", None):
            try:
                submitted_date = sub.completed_at.strftime("%d.%m.%Y %H:%M")
            except Exception:
                submitted_date = str(sub.completed_at)

        results.append({
            "id": sub.id,
            "user_id": sub.user_id,
            "employee_name": emp_name,
            "username": usr.username if usr else "-",
            "team_id": emp.team_id if emp else None,
            "team_name": team_name,
            "job_title": job_title,
            "score": sub.score,
            "total_questions": total,
            "percentage": percentage,
            "is_completed": sub.is_completed,
            "submitted_at": submitted_date
        })

    return results


@router.post("/quizzes/{quiz_id}/submit")
def submit_quiz(
    quiz_id: int,
    data: QuizSubmitSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz bulunamadı.")

    if current_user.company_id and quiz.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Bu teste erişim izniniz yok.")

    existing = (
        db.query(QuizSubmission)
        .filter(QuizSubmission.quiz_id == quiz_id, QuizSubmission.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Bu quiz zaten tamamlandı.")

    score = 0
    questions = quiz.questions or []
    for idx, ques in enumerate(questions):
        if idx < len(data.selected_answers):
            if data.selected_answers[idx] == ques.get("correct_index"):
                score += 1

    submission = QuizSubmission(
        quiz_id=quiz_id,
        user_id=current_user.id,
        score=score,
        total_questions=len(questions),
        is_completed=True,
    )
    db.add(submission)
    db.commit()
    return {"score": score, "total_questions": len(questions), "message": "Quiz başarıyla gönderildi."}


# ================= SHIFT & BREAK ENDPOINTS =================

@router.post("/shifts")
def save_company_shift(
    data: ShiftSaveSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_manager_or_owner),
):
    today = data.shift_date or date.today().isoformat()
    company_id = current_user.company_id

    # Takım lideri kontrolü
    if current_user.role == UserRole.TAKIM_LIDERI.value and data.employee_id:
        leader_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        target_emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
        if not leader_emp or not target_emp or leader_emp.team_id != target_emp.team_id:
            raise HTTPException(
                status_code=403,
                detail="Yalnızca kendi takımınızdaki personelin vardiyasını düzenleyebilirsiniz."
            )

    shift = (
        db.query(ShiftSchedule)
        .filter(
            ShiftSchedule.company_id == company_id,
            ShiftSchedule.shift_date == today,
            ShiftSchedule.employee_id == data.employee_id
        )
        .first()
    )

    if not shift:
        shift = ShiftSchedule(
            company_id=company_id,
            employee_id=data.employee_id,
            shift_date=today,
            start_time=data.start_time,
            end_time=data.end_time,
            break_1=data.break_1,
            lunch_break=data.lunch_break,
            break_2=data.break_2,
            break_3=data.break_3,
        )
        db.add(shift)
    else:
        shift.start_time = data.start_time
        shift.end_time = data.end_time
        shift.break_1 = data.break_1
        shift.lunch_break = data.lunch_break
        shift.break_2 = data.break_2
        shift.break_3 = data.break_3

    db.commit()
    db.refresh(shift)
    return shift


@router.get("/shifts/today")
def get_today_shift(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today().isoformat()
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()

    shift = None
    if emp:
        shift = (
            db.query(ShiftSchedule)
            .filter(
                ShiftSchedule.company_id == current_user.company_id,
                ShiftSchedule.shift_date == today,
                ShiftSchedule.employee_id == emp.id
            )
            .first()
        )

    if not shift:
        shift = (
            db.query(ShiftSchedule)
            .filter(
                ShiftSchedule.company_id == current_user.company_id,
                ShiftSchedule.shift_date == today,
                ShiftSchedule.employee_id.is_(None)
            )
            .first()
        )

    if not shift:
        return {
            "shift_date": today,
            "employee_id": None,
            "start_time": "09:00",
            "end_time": "18:00",
            "break_1": "10:30 - 10:45",
            "lunch_break": "12:30 - 13:00",
            "break_2": "15:00 - 15:15",
            "break_3": "16:45 - 17:00",
        }
    return shift


@router.get("/shifts/daily-list")
def get_daily_shifts_list(
    shift_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_manager_or_owner),
):
    target_date = shift_date or date.today().isoformat()
    company_id = current_user.company_id or 1

    emp_query = db.query(Employee)
    if current_user.role != UserRole.PLATFORM_OWNER.value:
        emp_query = emp_query.join(User, User.id == Employee.user_id).filter(User.company_id == company_id)

    # Takım lideri ise sadece kendi takımını getir
    if current_user.role == UserRole.TAKIM_LIDERI.value:
        leader_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        leader_team_id = leader_emp.team_id if leader_emp else -1
        emp_query = emp_query.filter(Employee.team_id == leader_team_id)

    employees = emp_query.all()

    # Genel şirket varsayılanı var mı?
    default_shift = db.query(ShiftSchedule).filter(
        ShiftSchedule.company_id == company_id,
        ShiftSchedule.shift_date == target_date,
        ShiftSchedule.employee_id.is_(None)
    ).first()

    results = []
    for emp in employees:
        shift = db.query(ShiftSchedule).filter(
            ShiftSchedule.company_id == company_id,
            ShiftSchedule.shift_date == target_date,
            ShiftSchedule.employee_id == emp.id
        ).first()

        active_shift = shift or default_shift
        team_name = emp.team.name if emp.team else "Genel Ekip"
        job_title = getattr(emp, "position", None) or getattr(emp, "job_title", "Personel")

        results.append({
            "employee_id": emp.id,
            "tc_no": emp.tc_no,
            "full_name": f"{emp.first_name} {emp.last_name}",
            "team_name": team_name,
            "job_title": job_title,
            "shift_date": target_date,
            "start_time": active_shift.start_time if active_shift else "09:00",
            "end_time": active_shift.end_time if active_shift else "18:00",
            "break_1": active_shift.break_1 if active_shift else "10:30 - 10:45",
            "lunch_break": active_shift.lunch_break if active_shift else "12:30 - 13:00",
            "break_2": active_shift.break_2 if active_shift else "15:00 - 15:15",
            "break_3": active_shift.break_3 if active_shift else "16:45 - 17:00",
        })

    return results
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.quiz_and_shift import Quiz, QuizSubmission, ShiftSchedule
from app.models.user import User
from app.models.employee import Employee
from app.security.auth_dependency import get_current_user, require_manager_or_owner
from app.security.user_role import UserRole

router = APIRouter(prefix="/operations", tags=["Quiz and Shifts"])


class QuizCreateSchema(BaseModel):
    title: str
    description: Optional[str] = ""
    duration_minutes: int = 15
    questions: list


class QuizSubmitSchema(BaseModel):
    selected_answers: list[int]


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
    current_user: User = Depends(require_manager_or_owner),
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Hesabınız bir şirkete bağlı değil.")

    quiz = Quiz(
        company_id=current_user.company_id,
        title=data.title,
        description=data.description,
        duration_minutes=data.duration_minutes,
        questions=data.questions,
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
    quizzes = (
        db.query(Quiz)
        .filter(Quiz.company_id == current_user.company_id, Quiz.is_active == True)
        .all()
    )
    submissions = {
        s.quiz_id: s
        for s in db.query(QuizSubmission).filter(QuizSubmission.user_id == current_user.id).all()
    }

    result = []
    for q in quizzes:
        sub = submissions.get(q.id)
        safe_questions = []
        for ques in q.questions:
            item = {
                "text": ques.get("text"),
                "options": ques.get("options", []),
            }
            if current_user.role in [UserRole.YONETICI.value, UserRole.PLATFORM_OWNER.value]:
                item["correct_index"] = ques.get("correct_index")
            safe_questions.append(item)

        result.append(
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "duration_minutes": q.duration_minutes,
                "total_questions": len(q.questions),
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
    current_user: User = Depends(require_manager_or_owner),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.company_id == current_user.company_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz bulunamadı.")

    submissions = (
        db.query(QuizSubmission, User, Employee)
        .join(User, User.id == QuizSubmission.user_id)
        .outerjoin(Employee, Employee.user_id == User.id)
        .filter(QuizSubmission.quiz_id == quiz_id)
        .all()
    )

    results = []
    for sub, usr, emp in submissions:
        emp_name = f"{emp.first_name} {emp.last_name}" if emp else usr.username
        job_title = emp.job_title if emp else "Belirtilmedi"
        percentage = round((sub.score / sub.total_questions) * 100, 1) if sub.total_questions else 0

        results.append({
            "id": sub.id,
            "employee_name": emp_name,
            "username": usr.username,
            "job_title": job_title,
            "score": sub.score,
            "total_questions": sub.total_questions,
            "percentage": percentage,
            "is_completed": sub.is_completed,
            "submitted_at": getattr(sub, "completed_at", None) or "Tamamlandı"
        })

    return results


@router.post("/quizzes/{quiz_id}/submit")
def submit_quiz(
    quiz_id: int,
    data: QuizSubmitSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = (
        db.query(Quiz)
        .filter(Quiz.id == quiz_id, Quiz.company_id == current_user.company_id)
        .first()
    )
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz bulunamadı.")

    existing = (
        db.query(QuizSubmission)
        .filter(QuizSubmission.quiz_id == quiz_id, QuizSubmission.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Bu quiz zaten tamamlandı.")

    score = 0
    for idx, ques in enumerate(quiz.questions):
        if idx < len(data.selected_answers):
            if data.selected_answers[idx] == ques.get("correct_index"):
                score += 1

    submission = QuizSubmission(
        quiz_id=quiz_id,
        user_id=current_user.id,
        score=score,
        total_questions=len(quiz.questions),
        is_completed=True,
    )
    db.add(submission)
    db.commit()
    return {"score": score, "total_questions": len(quiz.questions), "message": "Quiz başarıyla gönderildi."}


# ================= SHIFT & BREAK ENDPOINTS =================
@router.post("/shifts")
def save_company_shift(
    data: ShiftSaveSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_owner),
):
    today = data.shift_date or date.today().isoformat()

    shift = (
        db.query(ShiftSchedule)
        .filter(
            ShiftSchedule.company_id == current_user.company_id,
            ShiftSchedule.shift_date == today,
            ShiftSchedule.employee_id == data.employee_id
        )
        .first()
    )

    if not shift:
        shift = ShiftSchedule(
            company_id=current_user.company_id,
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
    # 1. Personele özel tanımlanmış vardiya var mı?
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

    # 2. Personele özel yoksa şirketin genel vardiyasını al
    if not shift:
        shift = (
            db.query(ShiftSchedule)
            .filter(
                ShiftSchedule.company_id == current_user.company_id,
                ShiftSchedule.shift_date == today,
                ShiftSchedule.employee_id == None
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
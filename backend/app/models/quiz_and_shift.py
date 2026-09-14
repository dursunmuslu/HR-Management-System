from datetime import datetime, timezone
from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from app.database.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=15)
    # [{"id": 1, "text": "Soru?", "options": ["A", "B", "C"], "correct_index": 0}]
    questions = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=True)
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ShiftSchedule(Base):
    __tablename__ = "shift_schedules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(Integer, nullable=True)
    shift_date = Column(String(10), nullable=False)
    start_time = Column(String(5), default="09:00")
    end_time = Column(String(5), default="18:00")
    # 3x 15 dk standart mola + 1x 30 dk yemek molası
    break_1 = Column(String(20), default="10:30 - 10:45")
    lunch_break = Column(String(20), default="12:30 - 13:00")
    break_2 = Column(String(20), default="15:00 - 15:15")
    break_3 = Column(String(20), default="16:45 - 17:00")
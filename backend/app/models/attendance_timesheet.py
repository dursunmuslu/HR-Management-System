from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database.database import Base


class AttendanceTimesheet(Base):
    __tablename__ = "attendance_timesheets"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)

    work_date = Column(Date, nullable=False, index=True)
    expected_minutes = Column(Integer, default=540)  # 9 saat = 540 dk
    actual_minutes = Column(Integer, default=0)
    diff_minutes = Column(Integer, default=0)  # Eksi ise eksik süre, artı ise fazla mesai
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee")


class PerformanceSurveyScore(Base):
    __tablename__ = "performance_survey_scores"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)

    period_month = Column(String(20), nullable=False, index=True)  # Örn: '2026-09'
    survey_type = Column(String(100), default="Müşteri Memnuniyeti (CSAT)")
    target_score = Column(Float, default=85.0)
    actual_score = Column(Float, default=0.0)
    survey_count = Column(Integer, default=1)
    feedback_note = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee")
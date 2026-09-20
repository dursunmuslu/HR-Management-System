from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    code = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    tax_number = Column(
        String(30),
        unique=True,
        nullable=True,
    )

    address = Column(
        String(500),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    # ============================================================
    # ŞİRKET MODÜL ERİŞİM AYARLARI
    # ============================================================
    is_announcements_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_quizzes_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_shifts_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_leaves_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_timesheets_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    suspended_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    suspension_reason = Column(
        String(500),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    users = relationship(
        "User",
        back_populates="company",
    )

    departments = relationship(
        "Department",
        back_populates="company",
        cascade="all, delete-orphan",
    )
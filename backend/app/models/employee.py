from datetime import date

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    team_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "teams.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    tc_no: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False,
    )

    employee_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    # Geçiş tamamlanana kadar korunacak.
    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    position: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    hire_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    remaining_annual_leave: Mapped[int] = mapped_column(
        Integer,
        default=14,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="employee",
    )

    team = relationship(
        "Team",
        back_populates="employees",
    )

    leave_requests = relationship(
        "LeaveRequest",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
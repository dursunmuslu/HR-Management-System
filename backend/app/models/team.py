from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # Takım Lideri (Employee tablosuna bağlanır)
    team_leader_id = Column(
        Integer,
        ForeignKey(
            "employees.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
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

    department = relationship(
        "Department",
        back_populates="teams",
    )

    # Takımın personelleri
    employees = relationship(
        "Employee",
        back_populates="team",
        foreign_keys="Employee.team_id",
    )

    # Takımın lideri (Employee objesi)
    team_leader = relationship(
        "Employee",
        foreign_keys=[team_leader_id],
        uselist=False,
    )
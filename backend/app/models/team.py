from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Team(Base):
    __tablename__ = "teams"

    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "name",
            name="uq_team_department_name",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        String(500),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    department = relationship(
        "Department",
        back_populates="teams",
    )
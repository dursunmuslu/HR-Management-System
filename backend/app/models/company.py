from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
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
    )

    departments = relationship(
        "Department",
        back_populates="company",
        cascade="all, delete-orphan",
    )
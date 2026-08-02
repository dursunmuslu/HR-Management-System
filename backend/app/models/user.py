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
from app.security.user_role import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # PLATFORM_OWNER herhangi bir şirkete bağlı değildir.
    # YONETICI ve PERSONEL için zorunlu olacaktır.
    company_id = Column(
        Integer,
        ForeignKey(
            "companies.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    password = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        String(30),
        nullable=False,
        default=UserRole.PERSONEL.value,
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    must_change_password = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    password_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_at = Column(
        DateTime(timezone=True),
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

    company = relationship(
        "Company",
        back_populates="users",
    )

    employee = relationship(
        "Employee",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def is_platform_owner(self) -> bool:
        return (
            self.role ==
            UserRole.PLATFORM_OWNER.value
        )

    @property
    def is_company_manager(self) -> bool:
        return (
            self.role ==
            UserRole.YONETICI.value
        )

    @property
    def is_employee(self) -> bool:
        return (
            self.role ==
            UserRole.PERSONEL.value
        )
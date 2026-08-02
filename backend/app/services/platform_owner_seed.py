import os

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)
from app.security.password import hash_password
from app.security.user_role import UserRole


def create_platform_owner(
    db: Session,
) -> None:
    username = os.getenv(
        "PLATFORM_OWNER_USERNAME",
        "",
    ).strip().lower()

    password = os.getenv(
        "PLATFORM_OWNER_PASSWORD",
        "",
    )

    if not username or not password:
        print(
            "Platform owner seed skipped: "
            "environment variables are missing."
        )
        return

    if len(password) < 8:
        raise RuntimeError(
            "PLATFORM_OWNER_PASSWORD must contain "
            "at least 8 characters."
        )

    existing_owner = (
        db.query(User)
        .filter(
            User.role ==
            UserRole.PLATFORM_OWNER.value
        )
        .first()
    )

    if existing_owner is not None:
        return

    existing_username = (
        UserRepository.find_by_username(
            db,
            username,
        )
    )

    if existing_username is not None:
        existing_username.company_id = None
        existing_username.role = (
            UserRole.PLATFORM_OWNER.value
        )
        existing_username.is_active = True
        existing_username.must_change_password = (
            False
        )

        db.commit()
        db.refresh(existing_username)

        print(
            "Existing user promoted to "
            "platform owner."
        )

        return

    owner = User(
        company_id=None,
        username=username,
        password=hash_password(password),
        role=UserRole.PLATFORM_OWNER.value,
        is_active=True,
        must_change_password=False,
    )

    try:
        db.add(owner)
        db.commit()
        db.refresh(owner)

        print(
            "Platform owner account created."
        )

    except Exception:
        db.rollback()
        raise
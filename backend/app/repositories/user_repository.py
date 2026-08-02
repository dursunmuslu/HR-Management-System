from sqlalchemy import func
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.user import User
from app.security.user_role import UserRole


class UserRepository:

    @staticmethod
    def find_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        return (
            db.query(User)
            .options(
                joinedload(User.company),
                joinedload(User.employee),
            )
            .filter(
                User.id == user_id
            )
            .first()
        )

    @staticmethod
    def find_by_id_and_company(
        db: Session,
        user_id: int,
        company_id: int,
    ) -> User | None:
        return (
            db.query(User)
            .options(
                joinedload(User.company),
                joinedload(User.employee),
            )
            .filter(
                User.id == user_id,
                User.company_id == company_id,
            )
            .first()
        )

    @staticmethod
    def find_by_username(
        db: Session,
        username: str,
    ) -> User | None:
        normalized_username = (
            username
            .strip()
            .lower()
        )

        return (
            db.query(User)
            .options(
                joinedload(User.company),
                joinedload(User.employee),
            )
            .filter(
                func.lower(User.username)
                == normalized_username
            )
            .first()
        )

    @staticmethod
    def find_all_by_company(
        db: Session,
        company_id: int,
    ) -> list[User]:
        return (
            db.query(User)
            .options(
                joinedload(User.employee)
            )
            .filter(
                User.company_id == company_id
            )
            .order_by(
                User.username.asc()
            )
            .all()
        )

    @staticmethod
    def find_platform_owner(
        db: Session,
    ) -> User | None:
        return (
            db.query(User)
            .filter(
                User.role ==
                UserRole.PLATFORM_OWNER.value
            )
            .first()
        )

    @staticmethod
    def count_by_company(
        db: Session,
        company_id: int,
    ) -> int:
        return (
            db.query(func.count(User.id))
            .filter(
                User.company_id == company_id
            )
            .scalar()
            or 0
        )

    @staticmethod
    def count_by_company_and_role(
        db: Session,
        company_id: int,
        role: UserRole,
    ) -> int:
        return (
            db.query(func.count(User.id))
            .filter(
                User.company_id == company_id,
                User.role == role.value,
            )
            .scalar()
            or 0
        )

    @staticmethod
    def add(
        db: Session,
        user: User,
    ) -> User:
        """
        Kullanıcıyı transaction tamamlanmadan
        mevcut session'a ekler.

        User ve Employee gibi birden fazla kaydın
        tek transaction içinde oluşturulacağı
        işlemlerde kullanılır.
        """
        db.add(user)
        db.flush()

        return user

    @staticmethod
    def create(
        db: Session,
        user: User,
    ) -> User:
        try:
            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def save(
        db: Session,
        user: User,
    ) -> User:
        try:
            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except Exception:
            db.rollback()
            raise
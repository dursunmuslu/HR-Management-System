from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.user import User
from app.security.user_role import UserRole


class CompanyRepository:

    @staticmethod
    def find_all(
        db: Session,
    ) -> list[Company]:
        return (
            db.query(Company)
            .order_by(Company.name.asc())
            .all()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        company_id: int,
    ) -> Company | None:
        return (
            db.query(Company)
            .filter(
                Company.id == company_id
            )
            .first()
        )

    @staticmethod
    def find_by_name(
        db: Session,
        name: str,
    ) -> Company | None:
        return (
            db.query(Company)
            .filter(
                func.lower(Company.name)
                == name.lower()
            )
            .first()
        )

    @staticmethod
    def find_by_code(
        db: Session,
        code: str,
    ) -> Company | None:
        return (
            db.query(Company)
            .filter(
                func.lower(Company.code)
                == code.lower()
            )
            .first()
        )

    @staticmethod
    def find_by_tax_number(
        db: Session,
        tax_number: str,
    ) -> Company | None:
        return (
            db.query(Company)
            .filter(
                Company.tax_number == tax_number
            )
            .first()
        )

    @staticmethod
    def count_all(
        db: Session,
    ) -> int:
        return (
            db.query(func.count(Company.id))
            .scalar()
            or 0
        )

    @staticmethod
    def count_active(
        db: Session,
    ) -> int:
        return (
            db.query(func.count(Company.id))
            .filter(Company.is_active.is_(True))
            .scalar()
            or 0
        )

    @staticmethod
    def count_suspended(
        db: Session,
    ) -> int:
        return (
            db.query(func.count(Company.id))
            .filter(Company.is_active.is_(False))
            .scalar()
            or 0
        )

    @staticmethod
    def count_users(
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
    def count_managers(
        db: Session,
        company_id: int,
    ) -> int:
        return (
            db.query(func.count(User.id))
            .filter(
                User.company_id == company_id,
                User.role == UserRole.YONETICI.value,
            )
            .scalar()
            or 0
        )

    @staticmethod
    def count_employees(
        db: Session,
        company_id: int,
    ) -> int:
        return (
            db.query(func.count(User.id))
            .filter(
                User.company_id == company_id,
                User.role == UserRole.PERSONEL.value,
            )
            .scalar()
            or 0
        )

    @staticmethod
    def save(
        db: Session,
        company: Company,
    ) -> Company:
        try:
            db.add(company)
            db.commit()
            db.refresh(company)

            return company

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete(
        db: Session,
        company: Company,
    ) -> None:
        try:
            db.delete(company)
            db.commit()

        except Exception:
            db.rollback()
            raise
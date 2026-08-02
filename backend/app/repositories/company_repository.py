from sqlalchemy.orm import Session

from app.models.company import Company


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
            .filter(Company.id == company_id)
            .first()
        )

    @staticmethod
    def find_by_name(
        db: Session,
        name: str,
    ) -> Company | None:
        return (
            db.query(Company)
            .filter(Company.name == name)
            .first()
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
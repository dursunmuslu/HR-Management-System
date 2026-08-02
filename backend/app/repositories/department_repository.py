from sqlalchemy.orm import Session

from app.models.department import Department


class DepartmentRepository:

    @staticmethod
    def find_all(
        db: Session,
    ) -> list[Department]:
        return (
            db.query(Department)
            .order_by(Department.name.asc())
            .all()
        )

    @staticmethod
    def find_by_company_id(
        db: Session,
        company_id: int,
    ) -> list[Department]:
        return (
            db.query(Department)
            .filter(
                Department.company_id == company_id
            )
            .order_by(Department.name.asc())
            .all()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        department_id: int,
    ) -> Department | None:
        return (
            db.query(Department)
            .filter(
                Department.id == department_id
            )
            .first()
        )

    @staticmethod
    def find_by_company_and_name(
        db: Session,
        company_id: int,
        name: str,
    ) -> Department | None:
        return (
            db.query(Department)
            .filter(
                Department.company_id == company_id,
                Department.name == name,
            )
            .first()
        )

    @staticmethod
    def save(
        db: Session,
        department: Department,
    ) -> Department:
        try:
            db.add(department)
            db.commit()
            db.refresh(department)
            return department

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete(
        db: Session,
        department: Department,
    ) -> None:
        try:
            db.delete(department)
            db.commit()

        except Exception:
            db.rollback()
            raise
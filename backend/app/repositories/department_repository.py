from sqlalchemy import func
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.department import Department
from app.models.team import Team


class DepartmentRepository:

    @staticmethod
    def _query_with_relations(
        db: Session,
    ):
        return (
            db.query(Department)
            .options(
                joinedload(Department.company),
                joinedload(Department.teams)
                .joinedload(Team.employees),
            )
        )

    @staticmethod
    def find_all_by_company(
        db: Session,
        company_id: int,
    ) -> list[Department]:
        return (
            DepartmentRepository
            ._query_with_relations(db)
            .filter(
                Department.company_id == company_id
            )
            .order_by(
                Department.name.asc()
            )
            .all()
        )

    @staticmethod
    def find_active_by_company(
        db: Session,
        company_id: int,
    ) -> list[Department]:
        return (
            DepartmentRepository
            ._query_with_relations(db)
            .filter(
                Department.company_id == company_id,
                Department.is_active.is_(True),
            )
            .order_by(
                Department.name.asc()
            )
            .all()
        )

    @staticmethod
    def find_by_id_and_company(
        db: Session,
        department_id: int,
        company_id: int,
    ) -> Department | None:
        return (
            DepartmentRepository
            ._query_with_relations(db)
            .filter(
                Department.id == department_id,
                Department.company_id == company_id,
            )
            .first()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        department_id: int,
    ) -> Department | None:
        return (
            DepartmentRepository
            ._query_with_relations(db)
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
        normalized_name = (
            name
            .strip()
            .lower()
        )

        return (
            DepartmentRepository
            ._query_with_relations(db)
            .filter(
                Department.company_id == company_id,
                func.lower(Department.name)
                == normalized_name,
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

            return (
                DepartmentRepository
                .find_by_id_and_company(
                    db=db,
                    department_id=department.id,
                    company_id=department.company_id,
                )
            )

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
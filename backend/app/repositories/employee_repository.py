from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.employee import Employee
from app.models.team import Team
from app.models.user import User


class EmployeeRepository:

    @staticmethod
    def _query_with_relations(
        db: Session,
    ):
        return (
            db.query(Employee)
            .options(
                joinedload(Employee.user)
                .joinedload(User.company),

                joinedload(Employee.team)
                .joinedload(Team.department),
            )
        )

    @staticmethod
    def find_all_by_company(
        db: Session,
        company_id: int,
    ) -> list[Employee]:
        return (
            EmployeeRepository
            ._query_with_relations(db)
            .join(
                User,
                Employee.user_id == User.id,
            )
            .filter(
                User.company_id == company_id
            )
            .order_by(
                Employee.first_name.asc(),
                Employee.last_name.asc(),
            )
            .all()
        )

    @staticmethod
    def find_by_id_and_company(
        db: Session,
        employee_id: int,
        company_id: int,
    ) -> Employee | None:
        return (
            EmployeeRepository
            ._query_with_relations(db)
            .join(
                User,
                Employee.user_id == User.id,
            )
            .filter(
                Employee.id == employee_id,
                User.company_id == company_id,
            )
            .first()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        employee_id: int,
    ) -> Employee | None:
        return (
            EmployeeRepository
            ._query_with_relations(db)
            .filter(
                Employee.id == employee_id
            )
            .first()
        )

    @staticmethod
    def find_by_user_id(
        db: Session,
        user_id: int,
    ) -> Employee | None:
        return (
            EmployeeRepository
            ._query_with_relations(db)
            .filter(
                Employee.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def find_by_tc_no(
        db: Session,
        tc_no: str,
    ) -> Employee | None:
        return (
            db.query(Employee)
            .filter(
                Employee.tc_no == tc_no
            )
            .first()
        )

    @staticmethod
    def find_by_employee_number(
        db: Session,
        employee_number: str,
    ) -> Employee | None:
        return (
            db.query(Employee)
            .filter(
                Employee.employee_number
                == employee_number
            )
            .first()
        )

    @staticmethod
    def find_by_email(
        db: Session,
        email: str,
    ) -> Employee | None:
        return (
            db.query(Employee)
            .filter(
                Employee.email == email
            )
            .first()
        )

    @staticmethod
    def add(
        db: Session,
        employee: Employee,
    ) -> Employee:
        db.add(employee)
        db.flush()

        return employee

    @staticmethod
    def save(
        db: Session,
        employee: Employee,
    ) -> Employee:
        try:
            db.add(employee)
            db.commit()
            db.refresh(employee)

            return employee

        except Exception:
            db.rollback()
            raise
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.employee import Employee


class EmployeeRepository:

    @staticmethod
    def find_all(
        db: Session,
    ) -> list[Employee]:
        return (
            db.query(Employee)
            .options(
                joinedload(Employee.user)
            )
            .order_by(
                Employee.first_name.asc(),
                Employee.last_name.asc(),
            )
            .all()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        employee_id: int,
    ) -> Employee | None:
        return (
            db.query(Employee)
            .options(
                joinedload(Employee.user)
            )
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
            db.query(Employee)
            .options(
                joinedload(Employee.user)
            )
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
    def create(
        db: Session,
        employee: Employee,
    ) -> Employee:
        try:
            db.add(employee)
            db.commit()
            db.refresh(employee)

            return (
                db.query(Employee)
                .options(
                    joinedload(Employee.user)
                )
                .filter(
                    Employee.id == employee.id
                )
                .first()
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def save(
        db: Session,
        employee: Employee,
    ) -> Employee:
        try:
            db.add(employee)
            db.commit()
            db.refresh(employee)

            return (
                db.query(Employee)
                .options(
                    joinedload(Employee.user)
                )
                .filter(
                    Employee.id == employee.id
                )
                .first()
            )

        except Exception:
            db.rollback()
            raise
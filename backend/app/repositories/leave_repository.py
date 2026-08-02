from datetime import date

from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.user import User
from app.security.leave_status import LeaveStatus


class LeaveRepository:

    @staticmethod
    def _query_with_relations(
        db: Session,
    ):
        return (
            db.query(LeaveRequest)
            .options(
                joinedload(LeaveRequest.employee)
                .joinedload(Employee.user)
                .joinedload(User.company),

                joinedload(LeaveRequest.employee)
                .joinedload(Employee.team),
            )
        )

    @staticmethod
    def find_all_by_company(
        db: Session,
        company_id: int,
    ) -> list[LeaveRequest]:
        return (
            LeaveRepository
            ._query_with_relations(db)
            .join(
                Employee,
                LeaveRequest.employee_id ==
                Employee.id,
            )
            .join(
                User,
                Employee.user_id == User.id,
            )
            .filter(
                User.company_id == company_id
            )
            .order_by(
                LeaveRequest.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def find_pending_by_company(
        db: Session,
        company_id: int,
    ) -> list[LeaveRequest]:
        return (
            LeaveRepository
            ._query_with_relations(db)
            .join(
                Employee,
                LeaveRequest.employee_id ==
                Employee.id,
            )
            .join(
                User,
                Employee.user_id == User.id,
            )
            .filter(
                User.company_id == company_id,
                LeaveRequest.status ==
                LeaveStatus.PENDING.value,
            )
            .order_by(
                LeaveRequest.created_at.asc()
            )
            .all()
        )

    @staticmethod
    def find_by_id_and_company(
        db: Session,
        leave_id: int,
        company_id: int,
    ) -> LeaveRequest | None:
        return (
            LeaveRepository
            ._query_with_relations(db)
            .join(
                Employee,
                LeaveRequest.employee_id ==
                Employee.id,
            )
            .join(
                User,
                Employee.user_id == User.id,
            )
            .filter(
                LeaveRequest.id == leave_id,
                User.company_id == company_id,
            )
            .first()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        leave_id: int,
    ) -> LeaveRequest | None:
        return (
            LeaveRepository
            ._query_with_relations(db)
            .filter(
                LeaveRequest.id == leave_id
            )
            .first()
        )

    @staticmethod
    def find_by_employee_id(
        db: Session,
        employee_id: int,
    ) -> list[LeaveRequest]:
        return (
            LeaveRepository
            ._query_with_relations(db)
            .filter(
                LeaveRequest.employee_id ==
                employee_id
            )
            .order_by(
                LeaveRequest.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def find_employee_leave_by_id(
        db: Session,
        employee_id: int,
        leave_id: int,
    ) -> LeaveRequest | None:
        return (
            LeaveRepository
            ._query_with_relations(db)
            .filter(
                LeaveRequest.id == leave_id,
                LeaveRequest.employee_id ==
                employee_id,
            )
            .first()
        )

    @staticmethod
    def find_overlapping_leave(
        db: Session,
        employee_id: int,
        start_date: date,
        end_date: date,
    ) -> LeaveRequest | None:
        return (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.employee_id ==
                employee_id,

                LeaveRequest.status.in_(
                    [
                        LeaveStatus.PENDING.value,
                        LeaveStatus.APPROVED.value,
                    ]
                ),

                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date,
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        leave_request: LeaveRequest,
    ) -> LeaveRequest:
        try:
            db.add(leave_request)
            db.commit()
            db.refresh(leave_request)

            return (
                LeaveRepository.find_by_id(
                    db=db,
                    leave_id=leave_request.id,
                )
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def save(
        db: Session,
        leave_request: LeaveRequest,
    ) -> LeaveRequest:
        try:
            db.add(leave_request)
            db.commit()
            db.refresh(leave_request)

            return (
                LeaveRepository.find_by_id(
                    db=db,
                    leave_id=leave_request.id,
                )
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def approve_with_employee_balance(
        db: Session,
        leave_request: LeaveRequest,
    ) -> LeaveRequest:
        try:
            db.add(leave_request)

            if leave_request.employee is not None:
                db.add(
                    leave_request.employee
                )

            db.flush()
            db.commit()

            db.refresh(leave_request)

            if leave_request.employee is not None:
                db.refresh(
                    leave_request.employee
                )

            return LeaveRepository.find_by_id(
                db=db,
                leave_id=leave_request.id,
            )

        except Exception:
            db.rollback()
            raise
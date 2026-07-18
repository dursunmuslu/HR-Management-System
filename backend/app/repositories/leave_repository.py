from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.models.leave_request import LeaveRequest
from app.security.leave_status import LeaveStatus


class LeaveRepository:

    @staticmethod
    def find_all(
        db: Session
    ) -> list[LeaveRequest]:
        return (
            db.query(LeaveRequest)
            .options(joinedload(LeaveRequest.employee))
            .order_by(LeaveRequest.created_at.desc())
            .all()
        )

    @staticmethod
    def find_pending(
        db: Session
    ) -> list[LeaveRequest]:
        return (
            db.query(LeaveRequest)
            .options(joinedload(LeaveRequest.employee))
            .filter(
                LeaveRequest.status
                == LeaveStatus.PENDING.value
            )
            .order_by(LeaveRequest.created_at.asc())
            .all()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        leave_id: int
    ) -> LeaveRequest | None:
        return (
            db.query(LeaveRequest)
            .options(joinedload(LeaveRequest.employee))
            .filter(LeaveRequest.id == leave_id)
            .first()
        )

    @staticmethod
    def find_by_employee_id(
        db: Session,
        employee_id: int
    ) -> list[LeaveRequest]:
        return (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.employee_id == employee_id
            )
            .order_by(LeaveRequest.created_at.desc())
            .all()
        )

    @staticmethod
    def find_employee_leave_by_id(
        db: Session,
        employee_id: int,
        leave_id: int
    ) -> LeaveRequest | None:
        return (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.id == leave_id,
                LeaveRequest.employee_id == employee_id
            )
            .first()
        )

    @staticmethod
    def find_overlapping_leave(
        db: Session,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> LeaveRequest | None:
        return (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status.in_(
                    [
                        LeaveStatus.PENDING.value,
                        LeaveStatus.APPROVED.value
                    ]
                ),
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        leave_request: LeaveRequest
    ) -> LeaveRequest:
        try:
            db.add(leave_request)
            db.commit()
            db.refresh(leave_request)

            return leave_request

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def save(
        db: Session,
        leave_request: LeaveRequest
    ) -> LeaveRequest:
        try:
            db.add(leave_request)
            db.commit()
            db.refresh(leave_request)

            return leave_request

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def approve_with_employee_balance(
        db: Session,
        leave_request: LeaveRequest
    ) -> LeaveRequest:
        try:
            db.add(leave_request)
            db.add(leave_request.employee)

            db.flush()
            db.commit()

            db.refresh(leave_request)
            db.refresh(leave_request.employee)

            return leave_request

        except Exception:
            db.rollback()
            raise
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.security.leave_status import LeaveStatus


class DashboardRepository:

    @staticmethod
    def count_employees(
        db: Session
    ) -> int:
        employee_count = (
            db.query(func.count(Employee.id))
            .scalar()
        )

        return employee_count or 0

    @staticmethod
    def count_all_leave_requests(
        db: Session
    ) -> int:
        leave_count = (
            db.query(func.count(LeaveRequest.id))
            .scalar()
        )

        return leave_count or 0

    @staticmethod
    def count_leave_requests_by_status(
        db: Session,
        leave_status: LeaveStatus
    ) -> int:
        leave_count = (
            db.query(func.count(LeaveRequest.id))
            .filter(
                LeaveRequest.status
                == leave_status.value
            )
            .scalar()
        )

        return leave_count or 0

    @staticmethod
    def sum_remaining_annual_leave(
        db: Session
    ) -> int:
        total_remaining_leave = (
            db.query(
                func.coalesce(
                    func.sum(
                        Employee.remaining_annual_leave
                    ),
                    0
                )
            )
            .scalar()
        )

        return int(total_remaining_leave or 0)
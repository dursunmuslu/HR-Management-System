from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.user import User
from app.security.leave_status import LeaveStatus


class DashboardRepository:

    @staticmethod
    def count_employees_by_company(
        db: Session,
        company_id: int,
    ) -> int:
        employee_count = (
            db.query(
                func.count(Employee.id)
            )
            .join(
                User,
                Employee.user_id == User.id,
            )
            .filter(
                User.company_id == company_id,
                User.is_active.is_(True),
            )
            .scalar()
        )

        return int(employee_count or 0)

    @staticmethod
    def count_all_leave_requests_by_company(
        db: Session,
        company_id: int,
    ) -> int:
        leave_count = (
            db.query(
                func.count(LeaveRequest.id)
            )
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
            .scalar()
        )

        return int(leave_count or 0)

    @staticmethod
    def count_leave_requests_by_company_and_status(
        db: Session,
        company_id: int,
        leave_status: LeaveStatus,
    ) -> int:
        leave_count = (
            db.query(
                func.count(LeaveRequest.id)
            )
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
                leave_status.value,
            )
            .scalar()
        )

        return int(leave_count or 0)

    @staticmethod
    def sum_remaining_annual_leave_by_company(
        db: Session,
        company_id: int,
    ) -> int:
        total_remaining_leave = (
            db.query(
                func.coalesce(
                    func.sum(
                        Employee.remaining_annual_leave
                    ),
                    0,
                )
            )
            .join(
                User,
                Employee.user_id == User.id,
            )
            .filter(
                User.company_id == company_id,
                User.is_active.is_(True),
            )
            .scalar()
        )

        return int(
            total_remaining_leave or 0
        )
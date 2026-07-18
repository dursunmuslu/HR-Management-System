from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import (
    DashboardRepository
)
from app.schemas.dashboard_schema import (
    DashboardSummaryResponse
)
from app.security.leave_status import LeaveStatus


class DashboardService:

    @staticmethod
    def get_summary(
        db: Session
    ) -> DashboardSummaryResponse:
        total_employees = (
            DashboardRepository.count_employees(db)
        )

        total_leave_requests = (
            DashboardRepository
            .count_all_leave_requests(db)
        )

        pending_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_status(
                db,
                LeaveStatus.PENDING
            )
        )

        approved_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_status(
                db,
                LeaveStatus.APPROVED
            )
        )

        rejected_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_status(
                db,
                LeaveStatus.REJECTED
            )
        )

        cancelled_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_status(
                db,
                LeaveStatus.CANCELLED
            )
        )

        total_remaining_annual_leave = (
            DashboardRepository
            .sum_remaining_annual_leave(db)
        )

        return DashboardSummaryResponse(
            total_employees=total_employees,
            total_leave_requests=(
                total_leave_requests
            ),
            pending_leave_requests=(
                pending_leave_requests
            ),
            approved_leave_requests=(
                approved_leave_requests
            ),
            rejected_leave_requests=(
                rejected_leave_requests
            ),
            cancelled_leave_requests=(
                cancelled_leave_requests
            ),
            total_remaining_annual_leave=(
                total_remaining_annual_leave
            )
        )
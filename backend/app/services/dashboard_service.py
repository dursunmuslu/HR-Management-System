from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.schemas.dashboard_schema import (
    DashboardSummaryResponse,
)
from app.security.leave_status import LeaveStatus


class DashboardService:

    @staticmethod
    def get_summary(
        db: Session,
        current_user: User,
    ) -> DashboardSummaryResponse:
        company_id = (
            DashboardService
            ._require_company_id(current_user)
        )

        total_employees = (
            DashboardRepository
            .count_employees_by_company(
                db=db,
                company_id=company_id,
            )
        )

        total_leave_requests = (
            DashboardRepository
            .count_all_leave_requests_by_company(
                db=db,
                company_id=company_id,
            )
        )

        pending_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_company_and_status(
                db=db,
                company_id=company_id,
                leave_status=LeaveStatus.PENDING,
            )
        )

        approved_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_company_and_status(
                db=db,
                company_id=company_id,
                leave_status=LeaveStatus.APPROVED,
            )
        )

        rejected_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_company_and_status(
                db=db,
                company_id=company_id,
                leave_status=LeaveStatus.REJECTED,
            )
        )

        cancelled_leave_requests = (
            DashboardRepository
            .count_leave_requests_by_company_and_status(
                db=db,
                company_id=company_id,
                leave_status=LeaveStatus.CANCELLED,
            )
        )

        total_remaining_annual_leave = (
            DashboardRepository
            .sum_remaining_annual_leave_by_company(
                db=db,
                company_id=company_id,
            )
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
            ),
        )

    @staticmethod
    def _require_company_id(
        current_user: User,
    ) -> int:
        if current_user.company_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "User account is not associated "
                    "with a company."
                ),
            )

        return current_user.company_id
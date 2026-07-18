from pydantic import BaseModel, ConfigDict


class DashboardSummaryResponse(BaseModel):
    total_employees: int
    total_leave_requests: int
    pending_leave_requests: int
    approved_leave_requests: int
    rejected_leave_requests: int
    cancelled_leave_requests: int
    total_remaining_annual_leave: int

    model_config = ConfigDict(
        from_attributes=True
    )
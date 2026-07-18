from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.security.leave_status import LeaveStatus
from app.security.leave_type import LeaveType


class LeaveCreate(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date

    description: str | None = Field(
        default=None,
        max_length=1000
    )


class LeaveApprove(BaseModel):
    manager_note: str | None = Field(
        default=None,
        max_length=1000
    )


class LeaveReject(BaseModel):
    manager_note: str = Field(
        min_length=3,
        max_length=1000
    )


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    number_of_days: int
    description: str | None
    status: LeaveStatus
    manager_note: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class LeaveEmployeeResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    employee_number: str
    department: str
    position: str

    model_config = ConfigDict(
        from_attributes=True
    )


class LeaveDetailResponse(LeaveResponse):
    employee: LeaveEmployeeResponse
from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)

from app.schemas.user_schema import UserResponse


class EmployeeCreate(BaseModel):
    user_id: int = Field(gt=0)

    first_name: str = Field(
        min_length=2,
        max_length=50,
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
    )

    tc_no: str = Field(
        min_length=11,
        max_length=11,
        pattern=r"^[0-9]{11}$",
    )

    employee_number: str = Field(
        min_length=2,
        max_length=20,
    )

    department: str = Field(
        min_length=2,
        max_length=100,
    )

    position: str = Field(
        min_length=2,
        max_length=100,
    )

    phone: str = Field(
        min_length=10,
        max_length=20,
    )

    email: EmailStr

    hire_date: date

    remaining_annual_leave: int = Field(
        default=14,
        ge=0,
    )


class EmployeeCreateWithUser(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    password: str = Field(
        min_length=6,
        max_length=72,
    )

    first_name: str = Field(
        min_length=2,
        max_length=50,
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
    )

    tc_no: str = Field(
        min_length=11,
        max_length=11,
        pattern=r"^[0-9]{11}$",
    )

    employee_number: str = Field(
        min_length=2,
        max_length=20,
    )

    department: str = Field(
        min_length=2,
        max_length=100,
    )

    position: str = Field(
        min_length=2,
        max_length=100,
    )

    phone: str = Field(
        min_length=10,
        max_length=20,
    )

    email: EmailStr

    hire_date: date

    remaining_annual_leave: int = Field(
        default=14,
        ge=0,
    )


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    tc_no: str | None = Field(
        default=None,
        min_length=11,
        max_length=11,
        pattern=r"^[0-9]{11}$",
    )

    employee_number: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )

    department: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    position: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=20,
    )

    email: EmailStr | None = None

    hire_date: date | None = None

    remaining_annual_leave: int | None = Field(
        default=None,
        ge=0,
    )


class EmployeeResponse(BaseModel):
    id: int
    user_id: int

    first_name: str
    last_name: str
    tc_no: str
    employee_number: str
    department: str
    position: str
    phone: str
    email: EmailStr
    hire_date: date
    remaining_annual_leave: int

    user: UserResponse

    model_config = ConfigDict(
        from_attributes=True,
    )


class EmployeeProfileResponse(BaseModel):
    id: int
    user_id: int

    first_name: str
    last_name: str
    employee_number: str
    department: str
    position: str
    phone: str
    email: EmailStr
    hire_date: date
    remaining_annual_leave: int

    user: UserResponse

    model_config = ConfigDict(
        from_attributes=True,
    )


class LeaveBalanceResponse(BaseModel):
    employee_id: int
    employee_number: str
    first_name: str
    last_name: str
    remaining_annual_leave: int
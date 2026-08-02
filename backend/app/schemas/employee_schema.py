from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)

from app.schemas.user_schema import UserResponse


class EmployeeCreateWithUser(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    temporary_password: str = Field(
        min_length=8,
        max_length=72,
    )

    team_id: int = Field(
        gt=0,
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
    team_id: int | None = Field(
        default=None,
        gt=0,
    )

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


class EmployeeDepartmentResponse(BaseModel):
    id: int
    company_id: int
    name: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class EmployeeTeamResponse(BaseModel):
    id: int
    department_id: int
    name: str
    is_active: bool

    department: EmployeeDepartmentResponse

    model_config = ConfigDict(
        from_attributes=True,
    )


class EmployeeResponse(BaseModel):
    id: int
    user_id: int
    team_id: int | None

    first_name: str
    last_name: str
    tc_no: str
    employee_number: str

    # Eski frontend geçiş sürecinde kullanmaya
    # devam edebilsin diye response içinde tutuluyor.
    department: str

    position: str
    phone: str
    email: EmailStr
    hire_date: date
    remaining_annual_leave: int

    user: UserResponse
    team: EmployeeTeamResponse | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class EmployeeProfileResponse(BaseModel):
    id: int
    user_id: int
    team_id: int | None

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
    team: EmployeeTeamResponse | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class LeaveBalanceResponse(BaseModel):
    employee_id: int
    employee_number: str
    first_name: str
    last_name: str
    remaining_annual_leave: int
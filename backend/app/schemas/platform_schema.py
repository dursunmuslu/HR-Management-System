from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class InitialCompanyAdminCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    temporary_password: str = Field(
        min_length=8,
        max_length=72,
    )


class CompanyWithAdminCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    code: str = Field(
        min_length=2,
        max_length=30,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    tax_number: str | None = Field(
        default=None,
        max_length=30,
    )

    address: str | None = Field(
        default=None,
        max_length=500,
    )

    admin: InitialCompanyAdminCreate


class CompanySuspendRequest(BaseModel):
    reason: str = Field(
        min_length=5,
        max_length=500,
    )


class CompanyStatusResponse(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool
    suspended_at: datetime | None
    suspension_reason: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class PlatformCompanyListItem(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    user_count: int
    manager_count: int
    employee_count: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class PlatformSummaryResponse(BaseModel):
    total_companies: int
    active_companies: int
    suspended_companies: int

    total_users: int
    total_managers: int
    total_employees: int


class CompanyCreationResponse(BaseModel):
    company_id: int
    company_name: str
    company_code: str

    admin_user_id: int
    admin_username: str

    must_change_password: bool

    message: str
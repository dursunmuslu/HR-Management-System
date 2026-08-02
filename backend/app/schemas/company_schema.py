from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class CompanyUpdate(BaseModel):
    """
    Şirket yöneticisinin kendi şirketinde
    güncelleyebileceği temel bilgiler.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    tax_number: str | None = Field(
        default=None,
        max_length=30,
    )

    address: str | None = Field(
        default=None,
        max_length=500,
    )


class CompanyResponse(BaseModel):
    id: int

    code: str
    name: str

    tax_number: str | None
    address: str | None

    is_active: bool

    suspended_at: datetime | None
    suspension_reason: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
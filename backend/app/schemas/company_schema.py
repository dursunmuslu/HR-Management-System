from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class CompanyCreate(BaseModel):
    name: str = Field(
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


class CompanyUpdate(BaseModel):
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

    is_active: bool | None = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    tax_number: str | None
    address: str | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
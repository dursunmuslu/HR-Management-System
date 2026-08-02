from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class DepartmentCreate(BaseModel):
    company_id: int = Field(gt=0)

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class DepartmentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    id: int
    company_id: int
    name: str
    description: str | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
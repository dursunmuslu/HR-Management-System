from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TeamCreate(BaseModel):
    department_id: int = Field(gt=0)

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class TeamUpdate(BaseModel):
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


class TeamResponse(BaseModel):
    id: int
    department_id: int
    name: str
    description: str | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
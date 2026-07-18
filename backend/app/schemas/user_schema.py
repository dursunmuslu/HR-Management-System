from pydantic import BaseModel, ConfigDict, Field

from app.security.user_role import UserRole


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )
    password: str = Field(
        min_length=6,
        max_length=72
    )


class ManagerCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )
    password: str = Field(
        min_length=6,
        max_length=72
    )


class UserLogin(BaseModel):
    username: str
    password: str


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.security.user_role import UserRole


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )


class ManagerCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )


class UserLogin(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )

    password: str = Field(
        min_length=1,
        max_length=72,
    )


class UserRoleUpdate(BaseModel):
    role: UserRole

    @model_validator(mode="after")
    def validate_assignable_role(
        self,
    ) -> "UserRoleUpdate":
        if self.role == UserRole.PLATFORM_OWNER:
            raise ValueError(
                "Platform owner role cannot be assigned "
                "through this endpoint."
            )

        return self


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=72,
    )

    new_password: str = Field(
        min_length=8,
        max_length=72,
    )

    new_password_confirmation: str = Field(
        min_length=8,
        max_length=72,
    )

    @model_validator(mode="after")
    def validate_passwords(
        self,
    ) -> "ChangePasswordRequest":
        if (
            self.new_password !=
            self.new_password_confirmation
        ):
            raise ValueError(
                "New password confirmation does not match."
            )

        if (
            self.current_password ==
            self.new_password
        ):
            raise ValueError(
                "New password must be different "
                "from the current password."
            )

        return self


class ResetUserPasswordRequest(BaseModel):
    temporary_password: str = Field(
        min_length=8,
        max_length=72,
    )


class UserResponse(BaseModel):
    id: int
    company_id: int | None

    username: str
    role: UserRole

    is_active: bool
    must_change_password: bool

    password_changed_at: datetime | None
    last_login_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    must_change_password: bool
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
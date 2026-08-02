from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.user_schema import (
    ChangePasswordRequest,
    ResetUserPasswordRequest,
    TokenResponse,
    UserLogin,
    UserResponse,
    UserRoleUpdate,
)
from app.security.auth_dependency import (
    get_current_user,
    require_manager_or_owner,
)
from app.security.user_role import UserRole
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: UserLogin,
    db: Session = Depends(get_db),
):
    return AuthService.login(
        db=db,
        request=request,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_profile(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user


@router.post(
    "/change-password",
    response_model=UserResponse,
)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return AuthService.change_password(
        db=db,
        current_user=current_user,
        request=request,
    )


@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse,
)
def update_user_role(
    user_id: int,
    request: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager_or_owner
    ),
):
    return AuthService.update_user_role(
        db=db,
        user_id=user_id,
        request=request,
        current_user=current_user,
    )


@router.post(
    "/users/{user_id}/reset-password",
    response_model=UserResponse,
)
def reset_user_password(
    user_id: int,
    request: ResetUserPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager_or_owner
    ),
):
    target_user = _get_manageable_user(
        db=db,
        user_id=user_id,
        current_user=current_user,
    )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Use the change-password endpoint "
                "to change your own password."
            ),
        )

    if (
        target_user.role ==
        UserRole.PLATFORM_OWNER.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Platform owner password cannot be "
                "reset through this endpoint."
            ),
        )

    return AuthService.reset_user_password(
        db=db,
        target_user=target_user,
        request=request,
    )


@router.patch(
    "/users/{user_id}/disable",
    response_model=UserResponse,
)
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager_or_owner
    ),
):
    target_user = _get_manageable_user(
        db=db,
        user_id=user_id,
        current_user=current_user,
    )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "You cannot disable your own account."
            ),
        )

    return AuthService.disable_user(
        db=db,
        target_user=target_user,
    )


@router.patch(
    "/users/{user_id}/activate",
    response_model=UserResponse,
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager_or_owner
    ),
):
    target_user = _get_manageable_user(
        db=db,
        user_id=user_id,
        current_user=current_user,
    )

    return AuthService.activate_user(
        db=db,
        target_user=target_user,
    )


def _get_manageable_user(
    db: Session,
    user_id: int,
    current_user: User,
) -> User:
    """
    Yönetilecek kullanıcıyı güvenli biçimde getirir.

    Kurallar:
    - Platform sahibi şirket kullanıcılarını yönetebilir.
    - Şirket yöneticisi yalnızca kendi şirketindeki
      kullanıcıları yönetebilir.
    - Platform sahibi hesabı bu endpoint'lerden
      yönetilemez.
    """

    target_user = UserRepository.find_by_id(
        db,
        user_id,
    )

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be found.",
        )

    if (
        target_user.role ==
        UserRole.PLATFORM_OWNER.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Platform owner account cannot be "
                "managed through this endpoint."
            ),
        )

    if (
        current_user.role ==
        UserRole.YONETICI.value
    ):
        if (
            current_user.company_id is None
            or target_user.company_id !=
            current_user.company_id
        ):
            # Başka şirkette kullanıcı bulunduğunu
            # açıklamamak için 404 döndürülür.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User could not be found.",
            )

    return target_user
from fastapi import (
    APIRouter,
    Depends,
    status
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user_schema import (
    ManagerCreate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserRoleUpdate
)
from app.security.auth_dependency import (
    get_current_user,
    require_manager
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: UserCreate,
    db: Session = Depends(get_db)
):
    return AuthService.register(
        db,
        request
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: UserLogin,
    db: Session = Depends(get_db)
):
    return AuthService.login(
        db,
        request
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def get_profile(
    current_user: User = Depends(
        get_current_user
    )
):
    return current_user


@router.post(
    "/register-manager",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_manager(
    request: ManagerCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager)
):
    return AuthService.register_manager(
        db,
        request
    )


@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse
)
def update_user_role(
    user_id: int,
    request: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    )
):
    return AuthService.update_user_role(
        db=db,
        user_id=user_id,
        request=request,
        current_user=current_user
    )
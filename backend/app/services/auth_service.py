from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    ManagerCreate,
    UserCreate,
    UserLogin,
    UserRoleUpdate,
)
from app.security.jwt_handler import create_access_token
from app.security.password import (
    hash_password,
    verify_password,
)
from app.security.user_role import UserRole


class AuthService:

    @staticmethod
    def register(
        db: Session,
        request: UserCreate,
    ) -> User:
        normalized_username = (
            request.username
            .strip()
            .lower()
        )

        existing_user = UserRepository.find_by_username(
            db,
            normalized_username,
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            )

        user = User(
            username=normalized_username,
            password=hash_password(
                request.password
            ),
            role=UserRole.PERSONEL.value,
        )

        try:
            return UserRepository.create(
                db,
                user
            )

        except IntegrityError as exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            ) from exception

    @staticmethod
    def register_manager(
        db: Session,
        request: ManagerCreate,
    ) -> User:
        normalized_username = (
            request.username
            .strip()
            .lower()
        )

        existing_user = UserRepository.find_by_username(
            db,
            normalized_username,
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            )

        manager = User(
            username=normalized_username,
            password=hash_password(
                request.password
            ),
            role=UserRole.YONETICI.value,
        )

        try:
            return UserRepository.create(
                db,
                manager
            )

        except IntegrityError as exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            ) from exception

    @staticmethod
    def login(
        db: Session,
        request: UserLogin,
    ) -> dict:
        normalized_username = (
            request.username
            .strip()
            .lower()
        )

        user = UserRepository.find_by_username(
            db,
            normalized_username,
        )

        credentials_are_invalid = (
            user is None
            or not verify_password(
                request.password,
                user.password,
            )
        )

        if credentials_are_invalid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        access_token = create_access_token(
            user.username
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }

    @staticmethod
    def update_user_role(
        db: Session,
        user_id: int,
        request: UserRoleUpdate,
        current_user: User,
    ) -> User:
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot change your own role.",
            )

        if user.role == request.role.value:
            return user

        user.role = request.role.value

        try:
            db.commit()
            db.refresh(user)

            return user

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User role could not be updated.",
            ) from exception
from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.user_schema import (
    ChangePasswordRequest,
    ResetUserPasswordRequest,
    UserLogin,
    UserRoleUpdate,
)
from app.security.jwt_handler import (
    create_access_token,
)
from app.security.password import (
    hash_password,
    verify_password,
)
from app.security.user_role import UserRole


class AuthService:

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

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled.",
            )

        # Platform sahibi herhangi bir şirkete bağlı değildir.
        if (
            user.role !=
            UserRole.PLATFORM_OWNER.value
        ):
            if user.company_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "User account is not associated "
                        "with a company."
                    ),
                )

            if user.company is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "The company associated with this "
                        "account could not be found."
                    ),
                )

            if not user.company.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Company access has been suspended. "
                        "Contact the platform administrator."
                    ),
                )

        user.last_login_at = datetime.now(
            timezone.utc
        )

        try:
            db.commit()
            db.refresh(user)

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Login information could not "
                    "be updated."
                ),
            ) from exception

        access_token = create_access_token(
            user.username
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "must_change_password": (
                user.must_change_password
            ),
            "user": user,
        }

    @staticmethod
    def change_password(
        db: Session,
        current_user: User,
        request: ChangePasswordRequest,
    ) -> User:
        if not verify_password(
            request.current_password,
            current_user.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        if verify_password(
            request.new_password,
            current_user.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "New password must be different "
                    "from the current password."
                ),
            )

        current_user.password = hash_password(
            request.new_password
        )

        current_user.must_change_password = False

        current_user.password_changed_at = (
            datetime.now(timezone.utc)
        )

        try:
            db.commit()
            db.refresh(current_user)

            return current_user

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail="Password could not be changed.",
            ) from exception

    @staticmethod
    def reset_user_password(
        db: Session,
        target_user: User,
        request: ResetUserPasswordRequest,
    ) -> User:
        target_user.password = hash_password(
            request.temporary_password
        )

        target_user.must_change_password = True
        target_user.password_changed_at = None

        try:
            db.commit()
            db.refresh(target_user)

            return target_user

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "User password could not be reset."
                ),
            ) from exception

    @staticmethod
    def update_user_role(
        db: Session,
        user_id: int,
        request: UserRoleUpdate,
        current_user: User,
    ) -> User:
        user = UserRepository.find_by_id(
            db,
            user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User could not be found.",
            )

        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "You cannot change your own role."
                ),
            )

        # Platform sahibi rolü bu endpoint üzerinden
        # atanamaz veya değiştirilemez.
        if (
            request.role ==
            UserRole.PLATFORM_OWNER
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Platform owner role cannot be "
                    "assigned through this endpoint."
                ),
            )

        if (
            user.role ==
            UserRole.PLATFORM_OWNER.value
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Platform owner role cannot be "
                    "changed through this endpoint."
                ),
            )

        # Şirket yöneticisi sadece kendi şirketindeki
        # kullanıcıların rollerini değiştirebilir.
        if (
            current_user.role ==
            UserRole.YONETICI.value
        ):
            if (
                current_user.company_id is None
                or user.company_id !=
                current_user.company_id
            ):
                # Başka şirkette kullanıcı bulunduğunu
                # açıklamamak için 404 dönüyoruz.
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User could not be found.",
                )

        # Platform sahibi şirket yöneticisi/personel
        # rol değişimi yapabilir fakat kullanıcı
        # şirkete bağlı olmak zorundadır.
        if (
            current_user.role ==
            UserRole.PLATFORM_OWNER.value
            and user.company_id is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "A company must be assigned before "
                    "changing this user's company role."
                ),
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
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "User role could not be updated."
                ),
            ) from exception

    @staticmethod
    def disable_user(
        db: Session,
        target_user: User,
    ) -> User:
        if (
            target_user.role ==
            UserRole.PLATFORM_OWNER.value
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Platform owner account cannot "
                    "be disabled."
                ),
            )

        target_user.is_active = False

        try:
            db.commit()
            db.refresh(target_user)

            return target_user

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "User account could not be disabled."
                ),
            ) from exception

    @staticmethod
    def activate_user(
        db: Session,
        target_user: User,
    ) -> User:
        if (
            target_user.role ==
            UserRole.PLATFORM_OWNER.value
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Platform owner account cannot "
                    "be modified through this endpoint."
                ),
            )

        target_user.is_active = True

        try:
            db.commit()
            db.refresh(target_user)

            return target_user

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "User account could not be activated."
                ),
            ) from exception
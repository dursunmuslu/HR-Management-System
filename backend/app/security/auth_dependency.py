from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)
from app.security.jwt_handler import (
    decode_access_token,
)
from app.security.user_role import UserRole


bearer_scheme = HTTPBearer(
    scheme_name="JWT Authentication",
    auto_error=True,
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    JWT içindeki kullanıcı adını çözer ve kullanıcıyı
    veritabanından yükler.

    Her istekte:
    - Kullanıcı aktif mi?
    - Şirket bağlantısı var mı?
    - Şirket aktif mi?

    kontrollerini uygular.
    """

    username = decode_access_token(
        credentials.credentials
    )

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user = UserRepository.find_by_username(
        db,
        username,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account could not be found.",
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
        user.role ==
        UserRole.PLATFORM_OWNER.value
    ):
        return user

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

    return user


def require_password_changed(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:
    """
    Geçici şifre kullanan hesapların yönetim ve
    uygulama endpoint'lerine erişmesini engeller.

    /auth/change-password endpoint'i bu dependency'yi
    kullanmamalıdır.
    """

    if current_user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Password change is required before "
                "using this resource."
            ),
        )

    return current_user


def require_platform_owner(
    current_user: User = Depends(
        require_password_changed
    ),
) -> User:
    """
    Yalnızca platform sahibine izin verir.
    """

    if (
        current_user.role !=
        UserRole.PLATFORM_OWNER.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Platform owner authorization "
                "is required."
            ),
        )

    return current_user


def require_manager(
    current_user: User = Depends(
        require_password_changed
    ),
) -> User:
    """
    Yalnızca şirket yöneticisine izin verir.
    """

    if (
        current_user.role !=
        UserRole.YONETICI.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Company manager authorization "
                "is required."
            ),
        )

    if current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Manager account is not associated "
                "with a company."
            ),
        )

    return current_user


def require_employee(
    current_user: User = Depends(
        require_password_changed
    ),
) -> User:
    """
    Yalnızca personel rolüne izin verir.
    """

    if (
        current_user.role !=
        UserRole.PERSONEL.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee authorization is required.",
        )

    if current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Employee account is not associated "
                "with a company."
            ),
        )

    return current_user


def require_manager_or_owner(
    current_user: User = Depends(
        require_password_changed
    ),
) -> User:
    """
    Şirket yöneticisi veya platform sahibine izin verir.
    """

    allowed_roles = {
        UserRole.PLATFORM_OWNER.value,
        UserRole.YONETICI.value,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Company manager or platform owner "
                "authorization is required."
            ),
        )

    return current_user


def require_company_user(
    current_user: User = Depends(
        require_password_changed
    ),
) -> User:
    """
    Şirkete bağlı yönetici ve personellere izin verir.
    Platform sahibi şirket içi endpoint'lere bu
    dependency üzerinden erişemez.
    """

    allowed_roles = {
        UserRole.YONETICI.value,
        UserRole.PERSONEL.value,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "A company user account is required "
                "for this resource."
            ),
        )

    if current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "User account is not associated "
                "with a company."
            ),
        )

    return current_user
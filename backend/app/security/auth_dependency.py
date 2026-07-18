from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.jwt_handler import decode_access_token
from app.security.user_role import UserRole


bearer_scheme = HTTPBearer(
    scheme_name="JWT Authentication"
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    username = decode_access_token(credentials.credentials)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = UserRepository.find_by_username(db, username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account could not be found.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.YONETICI.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager authorization is required."
        )

    return current_user
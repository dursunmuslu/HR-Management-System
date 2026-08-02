from getpass import getpass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import SessionLocal

# SQLAlchemy ilişkilerinin eksiksiz yüklenmesi için
# tüm modeller import edilir.
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.team import Team
from app.models.user import User

from app.security.password import hash_password
from app.security.user_role import UserRole


def create_platform_owner(
    db: Session,
) -> None:
    existing_owner = (
        db.query(User)
        .filter(
            User.role ==
            UserRole.PLATFORM_OWNER.value
        )
        .first()
    )

    if existing_owner is not None:
        raise RuntimeError(
            "Platform owner hesabı zaten mevcut. "
            "İkinci owner oluşturulamaz."
        )

    username = input(
        "Platform owner kullanıcı adı: "
    ).strip().lower()

    if len(username) < 3:
        raise ValueError(
            "Kullanıcı adı en az 3 karakter olmalıdır."
        )

    if len(username) > 50:
        raise ValueError(
            "Kullanıcı adı en fazla 50 karakter olmalıdır."
        )

    existing_username = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if existing_username is not None:
        raise RuntimeError(
            "Bu kullanıcı adı zaten kullanılıyor."
        )

    password = getpass(
        "Platform owner şifresi: "
    )

    password_confirmation = getpass(
        "Şifre tekrar: "
    )

    if password != password_confirmation:
        raise ValueError(
            "Şifreler eşleşmiyor."
        )

    if len(password) < 12:
        raise ValueError(
            "Şifre en az 12 karakter olmalıdır."
        )

    if len(
        password.encode("utf-8")
    ) > 72:
        raise ValueError(
            "Şifre en fazla 72 bayt olabilir."
        )

    owner = User(
        username=username,
        password=hash_password(
            password
        ),
        role=UserRole.PLATFORM_OWNER.value,
        company_id=None,
        is_active=True,
        must_change_password=False,
    )

    try:
        db.add(owner)
        db.commit()
        db.refresh(owner)

        print()
        print(
            "Platform owner hesabı "
            "başarıyla oluşturuldu."
        )
        print(
            f"Kullanıcı adı: {owner.username}"
        )
        print(
            f"Rol: {owner.role}"
        )

    except IntegrityError as exception:
        db.rollback()

        raise RuntimeError(
            "Owner hesabı oluşturulamadı. "
            "Kullanıcı adı veya başka bir "
            "benzersiz alan çakışıyor."
        ) from exception

    except Exception:
        db.rollback()
        raise


def main() -> None:
    db = SessionLocal()

    try:
        create_platform_owner(
            db
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
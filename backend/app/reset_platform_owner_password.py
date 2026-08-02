from getpass import getpass

from sqlalchemy.orm import Session

from app.database.database import SessionLocal

# SQLAlchemy ilişki sınıflarının mapper registry içine
# yüklenmesi için tüm modeller import edilir.
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.team import Team
from app.models.user import User

from app.security.password import hash_password
from app.security.user_role import UserRole


def reset_platform_owner_password(
    db: Session,
) -> None:
    owners = (
        db.query(User)
        .filter(
            User.role ==
            UserRole.PLATFORM_OWNER.value
        )
        .all()
    )

    if len(owners) == 0:
        raise RuntimeError(
            "Platform owner hesabı bulunamadı."
        )

    if len(owners) > 1:
        raise RuntimeError(
            "Birden fazla platform owner bulundu. "
            "İşlem güvenlik nedeniyle durduruldu."
        )

    owner = owners[0]

    print(
        f"Şifresi güncellenecek hesap: "
        f"{owner.username}"
    )

    new_password = getpass(
        "Yeni şifre: "
    )

    confirmation = getpass(
        "Yeni şifre tekrar: "
    )

    if new_password != confirmation:
        raise ValueError(
            "Şifreler eşleşmiyor."
        )

    if len(new_password) < 12:
        raise ValueError(
            "Şifre en az 12 karakter olmalıdır."
        )

    if len(
        new_password.encode("utf-8")
    ) > 72:
        raise ValueError(
            "Şifre UTF-8 olarak en fazla "
            "72 bayt olabilir."
        )

    owner.password = hash_password(
        new_password
    )

    owner.company_id = None
    owner.is_active = True
    owner.must_change_password = False
    owner.password_changed_at = None

    try:
        db.commit()
        db.refresh(owner)

        print()
        print(
            "Platform owner şifresi "
            "başarıyla güncellendi."
        )
        print(
            f"Kullanıcı adı: {owner.username}"
        )
        print(
            f"Rol: {owner.role}"
        )

    except Exception:
        db.rollback()
        raise


def main() -> None:
    db = SessionLocal()

    try:
        reset_platform_owner_password(
            db
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
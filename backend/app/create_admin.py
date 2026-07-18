import os

from app.database.database import SessionLocal
from app.models.user import User

# Bu import sende farklı olabilir.
# Login işleminde kullanılan şifre hash fonksiyonuyla aynı olmalıdır.
from app.core.security import get_password_hash


def create_initial_admin() -> None:
    username = os.getenv("INITIAL_ADMIN_USERNAME", "dursun")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "123456")

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_user:
            existing_user.role = "YONETICI"

            db.commit()
            db.refresh(existing_user)

            print(
                f"Başlangıç kullanıcısı zaten mevcut: "
                f"{username}. Rolü YONETICI olarak güncellendi."
            )
            return

        admin_user = User(
            username=username,
            hashed_password=get_password_hash(password),
            role="YONETICI",
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"Başlangıç yöneticisi oluşturuldu: {username}")

    except Exception as error:
        db.rollback()
        print(f"Başlangıç yöneticisi oluşturulamadı: {error}")
        raise

    finally:
        db.close()
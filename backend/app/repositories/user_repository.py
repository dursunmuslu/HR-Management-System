from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    @staticmethod
    def find_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def find_by_username(
        db: Session,
        username: str,
    ) -> User | None:
        normalized_username = username.strip().lower()

        return (
            db.query(User)
            .filter(User.username == normalized_username)
            .first()
        )

    @staticmethod
    def add(
        db: Session,
        user: User,
    ) -> User:
        """
        Transaction tamamlanmadan kullanıcıyı session'a ekler.

        create-with-user işleminde hem User hem Employee
        tek transaction içinde oluşturulabilsin diye kullanılır.
        """
        db.add(user)
        db.flush()

        return user

    @staticmethod
    def create(
        db: Session,
        user: User,
    ) -> User:
        try:
            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except Exception:
            db.rollback()
            raise
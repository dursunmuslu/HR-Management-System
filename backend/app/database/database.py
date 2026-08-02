from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.config.settings import settings


def normalize_database_url(
    database_url: str,
) -> str:
    """
    Bazı servisler eski biçimde postgres:// URL
    döndürebilir. SQLAlchemy psycopg2 için bunu
    postgresql:// biçimine çevirir.
    """

    normalized_url = (
        database_url
        .strip()
    )

    if normalized_url.startswith(
        "postgres://"
    ):
        normalized_url = (
            normalized_url.replace(
                "postgres://",
                "postgresql://",
                1,
            )
        )

    return normalized_url


DATABASE_URL = normalize_database_url(
    settings.DATABASE_URL
)


engine: Engine = create_engine(
    DATABASE_URL,

    # Kopmuş bağlantıları sorgudan önce kontrol eder.
    pool_pre_ping=True,

    # Uzun süre boşta kalan bağlantıların
    # yeniden oluşturulmasını sağlar.
    pool_recycle=1800,

    # Ana connection pool büyüklüğü.
    pool_size=5,

    # Yoğunluk anında geçici ek bağlantı sayısı.
    max_overflow=10,

    # Pool'dan bağlantı bekleme süresi.
    pool_timeout=30,

    # Üretimde SQL sorgularını loglama.
    echo=False,
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[
    Session,
    None,
    None,
]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
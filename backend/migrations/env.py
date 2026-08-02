from logging.config import fileConfig

from alembic import context
from sqlalchemy import (
    engine_from_config,
    pool,
)

from app.config.settings import settings
from app.database.database import Base

# Alembic bütün modelleri görsün.
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.team import Team
from app.models.user import User


config = context.config


if config.config_file_name is not None:
    fileConfig(
        config.config_file_name
    )


database_url = settings.DATABASE_URL

# alembic.ini içinde yüzde işareti
# interpolation karakteri olduğu için kaçırıyoruz.
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(
        config.config_ini_section,
        {}
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
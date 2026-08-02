"""add platform and tenant fields

Revision ID: BURAYA_MEVCUT_REVISION
Revises:
Create Date: 2026-08-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "e251adddcbef"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def has_column(
    inspector: sa.Inspector,
    table_name: str,
    column_name: str,
) -> bool:
    return any(
        column["name"] == column_name
        for column in inspector.get_columns(
            table_name
        )
    )


def has_index(
    inspector: sa.Inspector,
    table_name: str,
    index_name: str,
) -> bool:
    return any(
        index["name"] == index_name
        for index in inspector.get_indexes(
            table_name
        )
    )


def has_foreign_key(
    inspector: sa.Inspector,
    table_name: str,
    constraint_name: str,
) -> bool:
    return any(
        foreign_key.get("name")
        == constraint_name
        for foreign_key
        in inspector.get_foreign_keys(
            table_name
        )
    )


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    table_names = set(
        inspector.get_table_names()
    )

    # ---------------------------------------------
    # COMPANIES
    # ---------------------------------------------

    if "companies" not in table_names:
        op.create_table(
            "companies",
            sa.Column(
                "id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "code",
                sa.String(length=30),
                nullable=False,
            ),
            sa.Column(
                "name",
                sa.String(length=150),
                nullable=False,
            ),
            sa.Column(
                "tax_number",
                sa.String(length=30),
                nullable=True,
            ),
            sa.Column(
                "address",
                sa.String(length=500),
                nullable=True,
            ),
            sa.Column(
                "is_active",
                sa.Boolean(),
                server_default=sa.true(),
                nullable=False,
            ),
            sa.Column(
                "suspended_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.Column(
                "suspension_reason",
                sa.String(length=500),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
            sa.UniqueConstraint("name"),
            sa.UniqueConstraint("tax_number"),
        )

        op.create_index(
            "ix_companies_id",
            "companies",
            ["id"],
            unique=False,
        )

        op.create_index(
            "ix_companies_code",
            "companies",
            ["code"],
            unique=True,
        )

        op.create_index(
            "ix_companies_name",
            "companies",
            ["name"],
            unique=True,
        )

        op.create_index(
            "ix_companies_is_active",
            "companies",
            ["is_active"],
            unique=False,
        )

    else:
        if not has_column(
            inspector,
            "companies",
            "code",
        ):
            op.add_column(
                "companies",
                sa.Column(
                    "code",
                    sa.String(length=30),
                    nullable=True,
                ),
            )

            connection.execute(
                sa.text(
                    """
                    UPDATE companies
                    SET code = 'COMPANY-' || id
                    WHERE code IS NULL
                    """
                )
            )

            op.alter_column(
                "companies",
                "code",
                existing_type=sa.String(
                    length=30
                ),
                nullable=False,
            )

        if not has_column(
            inspector,
            "companies",
            "suspended_at",
        ):
            op.add_column(
                "companies",
                sa.Column(
                    "suspended_at",
                    sa.DateTime(timezone=True),
                    nullable=True,
                ),
            )

        if not has_column(
            inspector,
            "companies",
            "suspension_reason",
        ):
            op.add_column(
                "companies",
                sa.Column(
                    "suspension_reason",
                    sa.String(length=500),
                    nullable=True,
                ),
            )

        if not has_column(
            inspector,
            "companies",
            "created_at",
        ):
            op.add_column(
                "companies",
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
            )

        if not has_column(
            inspector,
            "companies",
            "updated_at",
        ):
            op.add_column(
                "companies",
                sa.Column(
                    "updated_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
            )

        inspector = sa.inspect(connection)

        if not has_index(
            inspector,
            "companies",
            "ix_companies_code",
        ):
            op.create_index(
                "ix_companies_code",
                "companies",
                ["code"],
                unique=True,
            )

        if not has_index(
            inspector,
            "companies",
            "ix_companies_is_active",
        ):
            op.create_index(
                "ix_companies_is_active",
                "companies",
                ["is_active"],
                unique=False,
            )

    # Hiç şirket yoksa eski kullanıcıları bağlamak
    # için geçici varsayılan şirket oluştur.
    company_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM companies
            """
        )
    ).scalar_one()

    if company_count == 0:
        connection.execute(
            sa.text(
                """
                INSERT INTO companies (
                    code,
                    name,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    'DEFAULT',
                    'Varsayılan Şirket',
                    TRUE,
                    NOW(),
                    NOW()
                )
                """
            )
        )

    default_company_id = (
        connection.execute(
            sa.text(
                """
                SELECT id
                FROM companies
                ORDER BY id ASC
                LIMIT 1
                """
            )
        ).scalar_one()
    )

    # ---------------------------------------------
    # USERS
    # ---------------------------------------------

    inspector = sa.inspect(connection)

    if not has_column(
        inspector,
        "users",
        "company_id",
    ):
        op.add_column(
            "users",
            sa.Column(
                "company_id",
                sa.Integer(),
                nullable=True,
            ),
        )

    if not has_column(
        inspector,
        "users",
        "is_active",
    ):
        op.add_column(
            "users",
            sa.Column(
                "is_active",
                sa.Boolean(),
                server_default=sa.true(),
                nullable=False,
            ),
        )

    if not has_column(
        inspector,
        "users",
        "must_change_password",
    ):
        op.add_column(
            "users",
            sa.Column(
                "must_change_password",
                sa.Boolean(),
                server_default=sa.false(),
                nullable=False,
            ),
        )

    if not has_column(
        inspector,
        "users",
        "password_changed_at",
    ):
        op.add_column(
            "users",
            sa.Column(
                "password_changed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    if not has_column(
        inspector,
        "users",
        "last_login_at",
    ):
        op.add_column(
            "users",
            sa.Column(
                "last_login_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    if not has_column(
        inspector,
        "users",
        "created_at",
    ):
        op.add_column(
            "users",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if not has_column(
        inspector,
        "users",
        "updated_at",
    ):
        op.add_column(
            "users",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    # Role alanı PLATFORM_OWNER değerini
    # rahatça tutabilsin.
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=20),
        type_=sa.String(length=30),
        existing_nullable=False,
    )

    inspector = sa.inspect(connection)

    if not has_index(
        inspector,
        "users",
        "ix_users_company_id",
    ):
        op.create_index(
            "ix_users_company_id",
            "users",
            ["company_id"],
            unique=False,
        )

    if not has_index(
        inspector,
        "users",
        "ix_users_role",
    ):
        op.create_index(
            "ix_users_role",
            "users",
            ["role"],
            unique=False,
        )

    if not has_foreign_key(
        inspector,
        "users",
        "fk_users_company_id_companies",
    ):
        op.create_foreign_key(
            "fk_users_company_id_companies",
            "users",
            "companies",
            ["company_id"],
            ["id"],
            ondelete="RESTRICT",
        )

    # Eski yönetici ve personelleri ilk şirkete bağla.
    # PLATFORM_OWNER şirketsiz kalacak.
    connection.execute(
        sa.text(
            """
            UPDATE users
            SET company_id = :company_id
            WHERE company_id IS NULL
              AND role <> 'PLATFORM_OWNER'
            """
        ),
        {
            "company_id": default_company_id
        },
    )

    # Mevcut kullanıcıları ilk girişte zorla
    # şifre değiştirmeye yönlendirmiyoruz.
    connection.execute(
        sa.text(
            """
            UPDATE users
            SET must_change_password = FALSE
            WHERE must_change_password IS NULL
            """
        )
    )

    # ---------------------------------------------
    # EMPLOYEES
    # ---------------------------------------------

    inspector = sa.inspect(connection)

    if not has_column(
        inspector,
        "employees",
        "team_id",
    ):
        op.add_column(
            "employees",
            sa.Column(
                "team_id",
                sa.Integer(),
                nullable=True,
            ),
        )

    inspector = sa.inspect(connection)

    if not has_index(
        inspector,
        "employees",
        "ix_employees_team_id",
    ):
        op.create_index(
            "ix_employees_team_id",
            "employees",
            ["team_id"],
            unique=False,
        )

    table_names = set(
        inspector.get_table_names()
    )

    if (
        "teams" in table_names
        and not has_foreign_key(
            inspector,
            "employees",
            "fk_employees_team_id_teams",
        )
    ):
        op.create_foreign_key(
            "fk_employees_team_id_teams",
            "employees",
            "teams",
            ["team_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # ---------------------------------------------
    # EMPLOYEES
    # ---------------------------------------------

    if has_column(
        inspector,
        "employees",
        "team_id",
    ):
        if has_foreign_key(
            inspector,
            "employees",
            "fk_employees_team_id_teams",
        ):
            op.drop_constraint(
                "fk_employees_team_id_teams",
                "employees",
                type_="foreignkey",
            )

        if has_index(
            inspector,
            "employees",
            "ix_employees_team_id",
        ):
            op.drop_index(
                "ix_employees_team_id",
                table_name="employees",
            )

        op.drop_column(
            "employees",
            "team_id",
        )

    # ---------------------------------------------
    # USERS
    # ---------------------------------------------

    inspector = sa.inspect(connection)

    if has_foreign_key(
        inspector,
        "users",
        "fk_users_company_id_companies",
    ):
        op.drop_constraint(
            "fk_users_company_id_companies",
            "users",
            type_="foreignkey",
        )

    if has_index(
        inspector,
        "users",
        "ix_users_company_id",
    ):
        op.drop_index(
            "ix_users_company_id",
            table_name="users",
        )

    if has_index(
        inspector,
        "users",
        "ix_users_role",
    ):
        op.drop_index(
            "ix_users_role",
            table_name="users",
        )

    user_columns = {
        column["name"]
        for column
        in inspector.get_columns("users")
    }

    for column_name in [
        "updated_at",
        "created_at",
        "last_login_at",
        "password_changed_at",
        "must_change_password",
        "is_active",
        "company_id",
    ]:
        if column_name in user_columns:
            op.drop_column(
                "users",
                column_name,
            )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=30),
        type_=sa.String(length=20),
        existing_nullable=False,
    )

    # Company alanlarını downgrade sırasında
    # silmiyoruz. Şirket ve organizasyon verisinin
    # kaybolmasını istemiyoruz.
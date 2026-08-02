from sqlalchemy import func
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.department import Department
from app.models.team import Team


class TeamRepository:

    @staticmethod
    def _query_with_relations(
        db: Session,
    ):
        return (
            db.query(Team)
            .options(
                joinedload(Team.department)
                .joinedload(Department.company),

                joinedload(Team.employees),
            )
        )

    @staticmethod
    def find_all_by_company(
        db: Session,
        company_id: int,
    ) -> list[Team]:
        return (
            TeamRepository
            ._query_with_relations(db)
            .join(
                Department,
                Team.department_id == Department.id,
            )
            .filter(
                Department.company_id == company_id
            )
            .order_by(
                Department.name.asc(),
                Team.name.asc(),
            )
            .all()
        )

    @staticmethod
    def find_active_by_company(
        db: Session,
        company_id: int,
    ) -> list[Team]:
        return (
            TeamRepository
            ._query_with_relations(db)
            .join(
                Department,
                Team.department_id == Department.id,
            )
            .filter(
                Department.company_id == company_id,
                Department.is_active.is_(True),
                Team.is_active.is_(True),
            )
            .order_by(
                Department.name.asc(),
                Team.name.asc(),
            )
            .all()
        )

    @staticmethod
    def find_by_department_and_company(
        db: Session,
        department_id: int,
        company_id: int,
    ) -> list[Team]:
        return (
            TeamRepository
            ._query_with_relations(db)
            .join(
                Department,
                Team.department_id == Department.id,
            )
            .filter(
                Team.department_id == department_id,
                Department.company_id == company_id,
            )
            .order_by(
                Team.name.asc()
            )
            .all()
        )

    @staticmethod
    def find_active_by_department_and_company(
        db: Session,
        department_id: int,
        company_id: int,
    ) -> list[Team]:
        return (
            TeamRepository
            ._query_with_relations(db)
            .join(
                Department,
                Team.department_id == Department.id,
            )
            .filter(
                Team.department_id == department_id,
                Department.company_id == company_id,
                Department.is_active.is_(True),
                Team.is_active.is_(True),
            )
            .order_by(
                Team.name.asc()
            )
            .all()
        )

    @staticmethod
    def find_by_id_and_company(
        db: Session,
        team_id: int,
        company_id: int,
    ) -> Team | None:
        return (
            TeamRepository
            ._query_with_relations(db)
            .join(
                Department,
                Team.department_id == Department.id,
            )
            .filter(
                Team.id == team_id,
                Department.company_id == company_id,
            )
            .first()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        team_id: int,
    ) -> Team | None:
        return (
            TeamRepository
            ._query_with_relations(db)
            .filter(
                Team.id == team_id
            )
            .first()
        )

    @staticmethod
    def find_by_department_and_name(
        db: Session,
        department_id: int,
        name: str,
    ) -> Team | None:
        normalized_name = (
            name
            .strip()
            .lower()
        )

        return (
            TeamRepository
            ._query_with_relations(db)
            .filter(
                Team.department_id == department_id,
                func.lower(Team.name)
                == normalized_name,
            )
            .first()
        )

    @staticmethod
    def save(
        db: Session,
        team: Team,
    ) -> Team:
        try:
            db.add(team)
            db.commit()
            db.refresh(team)

            return TeamRepository.find_by_id(
                db=db,
                team_id=team.id,
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete(
        db: Session,
        team: Team,
    ) -> None:
        try:
            db.delete(team)
            db.commit()

        except Exception:
            db.rollback()
            raise
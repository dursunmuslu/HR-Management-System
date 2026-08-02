from sqlalchemy.orm import Session

from app.models.team import Team


class TeamRepository:

    @staticmethod
    def find_all(
        db: Session,
    ) -> list[Team]:
        return (
            db.query(Team)
            .order_by(Team.name.asc())
            .all()
        )

    @staticmethod
    def find_by_department_id(
        db: Session,
        department_id: int,
    ) -> list[Team]:
        return (
            db.query(Team)
            .filter(
                Team.department_id == department_id
            )
            .order_by(Team.name.asc())
            .all()
        )

    @staticmethod
    def find_by_id(
        db: Session,
        team_id: int,
    ) -> Team | None:
        return (
            db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )

    @staticmethod
    def find_by_department_and_name(
        db: Session,
        department_id: int,
        name: str,
    ) -> Team | None:
        return (
            db.query(Team)
            .filter(
                Team.department_id == department_id,
                Team.name == name,
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
            return team

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
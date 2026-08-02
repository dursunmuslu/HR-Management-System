from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.team import Team
from app.repositories.department_repository import (
    DepartmentRepository,
)
from app.repositories.team_repository import (
    TeamRepository,
)
from app.schemas.team_schema import (
    TeamCreate,
    TeamUpdate,
)


class TeamService:

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Team]:
        return TeamRepository.find_all(db)

    @staticmethod
    def get_by_department(
        db: Session,
        department_id: int,
    ) -> list[Team]:
        department = DepartmentRepository.find_by_id(
            db,
            department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department could not be found.",
            )

        return TeamRepository.find_by_department_id(
            db,
            department_id,
        )

    @staticmethod
    def get_by_id(
        db: Session,
        team_id: int,
    ) -> Team:
        team = TeamRepository.find_by_id(
            db,
            team_id,
        )

        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team could not be found.",
            )

        return team

    @staticmethod
    def create(
        db: Session,
        request: TeamCreate,
    ) -> Team:
        department = DepartmentRepository.find_by_id(
            db,
            request.department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department could not be found.",
            )

        normalized_name = request.name.strip()

        existing_team = (
            TeamRepository
            .find_by_department_and_name(
                db,
                request.department_id,
                normalized_name,
            )
        )

        if existing_team is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A team with this name already "
                    "exists in the department."
                ),
            )

        team = Team(
            department_id=request.department_id,
            name=normalized_name,
            description=(
                request.description.strip()
                if request.description
                else None
            ),
        )

        return TeamRepository.save(
            db,
            team,
        )

    @staticmethod
    def update(
        db: Session,
        team_id: int,
        request: TeamUpdate,
    ) -> Team:
        team = TeamService.get_by_id(
            db,
            team_id,
        )

        update_data = request.model_dump(
            exclude_unset=True,
        )

        if "name" in update_data:
            normalized_name = update_data["name"].strip()

            existing_team = (
                TeamRepository
                .find_by_department_and_name(
                    db,
                    team.department_id,
                    normalized_name,
                )
            )

            if (
                existing_team is not None
                and existing_team.id != team.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A team with this name already "
                        "exists in the department."
                    ),
                )

            update_data["name"] = normalized_name

        if (
            "description" in update_data
            and update_data["description"] is not None
        ):
            update_data["description"] = (
                update_data["description"].strip()
            )

        for field_name, field_value in update_data.items():
            setattr(
                team,
                field_name,
                field_value,
            )

        return TeamRepository.save(
            db,
            team,
        )

    @staticmethod
    def delete(
        db: Session,
        team_id: int,
    ) -> None:
        team = TeamService.get_by_id(
            db,
            team_id,
        )

        TeamRepository.delete(
            db,
            team,
        )
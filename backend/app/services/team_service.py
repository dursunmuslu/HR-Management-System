from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.user import User
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
        current_user: User,
    ) -> list[Team]:
        company_id = (
            TeamService
            ._require_company_id(current_user)
        )

        return TeamRepository.find_all_by_company(
            db=db,
            company_id=company_id,
        )

    @staticmethod
    def get_by_department(
        db: Session,
        department_id: int,
        current_user: User,
    ) -> list[Team]:
        company_id = (
            TeamService
            ._require_company_id(current_user)
        )

        department = (
            DepartmentRepository
            .find_by_id_and_company(
                db=db,
                department_id=department_id,
                company_id=company_id,
            )
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department could not be found.",
            )

        return (
            TeamRepository
            .find_by_department_and_company(
                db=db,
                department_id=department_id,
                company_id=company_id,
            )
        )

    @staticmethod
    def get_by_id(
        db: Session,
        team_id: int,
        current_user: User,
    ) -> Team:
        company_id = (
            TeamService
            ._require_company_id(current_user)
        )

        team = TeamRepository.find_by_id_and_company(
            db=db,
            team_id=team_id,
            company_id=company_id,
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
        current_user: User,
    ) -> Team:
        company_id = (
            TeamService
            ._require_company_id(current_user)
        )

        department = (
            DepartmentRepository
            .find_by_id_and_company(
                db=db,
                department_id=request.department_id,
                company_id=company_id,
            )
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department could not be found.",
            )

        if not department.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A team cannot be created under "
                    "an inactive department."
                ),
            )

        normalized_name = (
            request.name.strip()
        )

        normalized_description = (
            request.description.strip()
            if request.description
            else None
        )

        existing_team = (
            TeamRepository
            .find_by_department_and_name(
                db=db,
                department_id=department.id,
                name=normalized_name,
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
            department_id=department.id,
            name=normalized_name,
            description=normalized_description,
            is_active=True,
        )

        return TeamRepository.save(
            db=db,
            team=team,
        )

    @staticmethod
    def update(
        db: Session,
        team_id: int,
        request: TeamUpdate,
        current_user: User,
    ) -> Team:
        team = TeamService.get_by_id(
            db=db,
            team_id=team_id,
            current_user=current_user,
        )

        update_data = request.model_dump(
            exclude_unset=True,
        )

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "At least one field must be "
                    "provided for update."
                ),
            )

        if "name" in update_data:
            normalized_name = (
                update_data["name"].strip()
            )

            existing_team = (
                TeamRepository
                .find_by_department_and_name(
                    db=db,
                    department_id=(
                        team.department_id
                    ),
                    name=normalized_name,
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

            update_data["name"] = (
                normalized_name
            )

        if (
            "description" in update_data
            and update_data["description"] is not None
        ):
            description = (
                update_data["description"].strip()
            )

            update_data["description"] = (
                description or None
            )

        for field_name, field_value in (
            update_data.items()
        ):
            setattr(
                team,
                field_name,
                field_value,
            )

        return TeamRepository.save(
            db=db,
            team=team,
        )

    @staticmethod
    def deactivate(
        db: Session,
        team_id: int,
        current_user: User,
    ) -> Team:
        team = TeamService.get_by_id(
            db=db,
            team_id=team_id,
            current_user=current_user,
        )

        if not team.is_active:
            return team

        team.is_active = False

        return TeamRepository.save(
            db=db,
            team=team,
        )

    @staticmethod
    def activate(
        db: Session,
        team_id: int,
        current_user: User,
    ) -> Team:
        team = TeamService.get_by_id(
            db=db,
            team_id=team_id,
            current_user=current_user,
        )

        if (
            team.department is None
            or not team.department.is_active
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "The department must be active "
                    "before activating the team."
                ),
            )

        if team.is_active:
            return team

        team.is_active = True

        return TeamRepository.save(
            db=db,
            team=team,
        )

    @staticmethod
    def delete(
        db: Session,
        team_id: int,
        current_user: User,
    ) -> None:
        team = TeamService.get_by_id(
            db=db,
            team_id=team_id,
            current_user=current_user,
        )

        if team.employees:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A team containing employees cannot "
                    "be deleted. Deactivate it instead."
                ),
            )

        TeamRepository.delete(
            db=db,
            team=team,
        )

    @staticmethod
    def _require_company_id(
        current_user: User,
    ) -> int:
        if current_user.company_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "User account is not associated "
                    "with a company."
                ),
            )

        return current_user.company_id
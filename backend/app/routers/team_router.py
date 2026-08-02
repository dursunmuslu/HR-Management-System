from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.team_schema import (
    TeamCreate,
    TeamResponse,
    TeamUpdate,
)
from app.security.auth_dependency import require_manager
from app.services.team_service import TeamService


router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.get(
    "",
    response_model=list[TeamResponse],
)
def get_teams(
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return TeamService.get_all(db)


@router.get(
    "/department/{department_id}",
    response_model=list[TeamResponse],
)
def get_teams_by_department(
    department_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return TeamService.get_by_department(
        db,
        department_id,
    )


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    request: TeamCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return TeamService.create(
        db,
        request,
    )


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
)
def update_team(
    team_id: int,
    request: TeamUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return TeamService.update(
        db,
        team_id,
        request,
    )


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    TeamService.delete(
        db,
        team_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
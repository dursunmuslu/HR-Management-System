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
from app.security.auth_dependency import (
    require_manager,
)
from app.services.team_service import (
    TeamService,
)


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
    current_user: User = Depends(
        require_manager
    ),
):
    return TeamService.get_all(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/department/{department_id}",
    response_model=list[TeamResponse],
)
def get_teams_by_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return TeamService.get_by_department(
        db=db,
        department_id=department_id,
        current_user=current_user,
    )


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return TeamService.get_by_id(
        db=db,
        team_id=team_id,
        current_user=current_user,
    )


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    request: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return TeamService.create(
        db=db,
        request=request,
        current_user=current_user,
    )


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
)
def update_team(
    team_id: int,
    request: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return TeamService.update(
        db=db,
        team_id=team_id,
        request=request,
        current_user=current_user,
    )


@router.patch(
    "/{team_id}/deactivate",
    response_model=TeamResponse,
)
def deactivate_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return TeamService.deactivate(
        db=db,
        team_id=team_id,
        current_user=current_user,
    )


@router.patch(
    "/{team_id}/activate",
    response_model=TeamResponse,
)
def activate_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return TeamService.activate(
        db=db,
        team_id=team_id,
        current_user=current_user,
    )


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    TeamService.delete(
        db=db,
        team_id=team_id,
        current_user=current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
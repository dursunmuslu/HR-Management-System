from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.security.auth_dependency import (
    require_manager,
)
from app.services.department_service import (
    DepartmentService,
)


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return DepartmentService.get_all(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return DepartmentService.get_by_id(
        db=db,
        department_id=department_id,
        current_user=current_user,
    )


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    request: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return DepartmentService.create(
        db=db,
        request=request,
        current_user=current_user,
    )


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: int,
    request: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return DepartmentService.update(
        db=db,
        department_id=department_id,
        request=request,
        current_user=current_user,
    )


@router.patch(
    "/{department_id}/deactivate",
    response_model=DepartmentResponse,
)
def deactivate_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return DepartmentService.deactivate(
        db=db,
        department_id=department_id,
        current_user=current_user,
    )


@router.patch(
    "/{department_id}/activate",
    response_model=DepartmentResponse,
)
def activate_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return DepartmentService.activate(
        db=db,
        department_id=department_id,
        current_user=current_user,
    )


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    DepartmentService.delete(
        db=db,
        department_id=department_id,
        current_user=current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
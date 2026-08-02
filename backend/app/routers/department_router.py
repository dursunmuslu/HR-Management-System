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
from app.security.auth_dependency import require_manager
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
    _: User = Depends(require_manager),
):
    return DepartmentService.get_all(db)


@router.get(
    "/company/{company_id}",
    response_model=list[DepartmentResponse],
)
def get_departments_by_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return DepartmentService.get_by_company(
        db,
        company_id,
    )


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    request: DepartmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return DepartmentService.create(
        db,
        request,
    )


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: int,
    request: DepartmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return DepartmentService.update(
        db,
        department_id,
        request,
    )


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    DepartmentService.delete(
        db,
        department_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
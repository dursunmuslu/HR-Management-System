from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.company_schema import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)
from app.security.auth_dependency import require_manager
from app.services.company_service import CompanyService


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get(
    "",
    response_model=list[CompanyResponse],
)
def get_companies(
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return CompanyService.get_all(db)


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return CompanyService.get_by_id(
        db,
        company_id,
    )


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    request: CompanyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return CompanyService.create(
        db,
        request,
    )


@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
)
def update_company(
    company_id: int,
    request: CompanyUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return CompanyService.update(
        db,
        company_id,
        request,
    )


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    CompanyService.delete(
        db,
        company_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.company_schema import (
    CompanyResponse,
    CompanyUpdate,
)
from app.security.auth_dependency import (
    require_manager,
)
from app.services.company_service import (
    CompanyService,
)


router = APIRouter(
    prefix="/companies",
    tags=["Company Profile"],
)


@router.get(
    "/me",
    response_model=CompanyResponse,
)
def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return CompanyService.get_my_company(
        db=db,
        current_user=current_user,
    )


@router.put(
    "/me",
    response_model=CompanyResponse,
)
def update_my_company(
    request: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_manager
    ),
):
    return CompanyService.update_my_company(
        db=db,
        request=request,
        current_user=current_user,
    )
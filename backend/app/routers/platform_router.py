from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.platform_schema import (
    CompanyCreationResponse,
    CompanyStatusResponse,
    CompanySuspendRequest,
    CompanyWithAdminCreate,
    PlatformCompanyListItem,
    PlatformSummaryResponse,
)
from app.security.auth_dependency import (
    require_platform_owner,
)
from app.services.platform_service import (
    PlatformService,
)


router = APIRouter(
    prefix="/platform",
    tags=["Platform Management"],
)


@router.get(
    "/summary",
    response_model=PlatformSummaryResponse,
)
def get_platform_summary(
    db: Session = Depends(get_db),
    _: User = Depends(
        require_platform_owner
    ),
):
    return PlatformService.get_summary(db)


@router.get(
    "/companies",
    response_model=list[
        PlatformCompanyListItem
    ],
)
def get_platform_companies(
    db: Session = Depends(get_db),
    _: User = Depends(
        require_platform_owner
    ),
):
    return PlatformService.get_companies(db)


@router.post(
    "/companies",
    response_model=CompanyCreationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company_with_admin(
    request: CompanyWithAdminCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_platform_owner
    ),
):
    return (
        PlatformService
        .create_company_with_admin(
            db,
            request,
        )
    )


@router.patch(
    "/companies/{company_id}/suspend",
    response_model=CompanyStatusResponse,
)
def suspend_company(
    company_id: int,
    request: CompanySuspendRequest,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_platform_owner
    ),
):
    return PlatformService.suspend_company(
        db,
        company_id,
        request,
    )


@router.patch(
    "/companies/{company_id}/activate",
    response_model=CompanyStatusResponse,
)
def activate_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_platform_owner
    ),
):
    return PlatformService.activate_company(
        db,
        company_id,
    )
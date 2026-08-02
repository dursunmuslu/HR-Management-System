from datetime import datetime, timezone

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.user import User
from app.repositories.company_repository import (
    CompanyRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.platform_schema import (
    CompanyCreationResponse,
    CompanySuspendRequest,
    CompanyWithAdminCreate,
    PlatformCompanyListItem,
    PlatformSummaryResponse,
)
from app.security.password import hash_password
from app.security.user_role import UserRole


class PlatformService:

    @staticmethod
    def get_summary(
        db: Session,
    ) -> PlatformSummaryResponse:
        total_users = (
            db.query(User)
            .filter(
                User.role !=
                UserRole.PLATFORM_OWNER.value
            )
            .count()
        )

        total_managers = (
            db.query(User)
            .filter(
                User.role ==
                UserRole.YONETICI.value
            )
            .count()
        )

        total_employees = (
            db.query(User)
            .filter(
                User.role ==
                UserRole.PERSONEL.value
            )
            .count()
        )

        return PlatformSummaryResponse(
            total_companies=(
                CompanyRepository.count_all(db)
            ),
            active_companies=(
                CompanyRepository.count_active(db)
            ),
            suspended_companies=(
                CompanyRepository.count_suspended(db)
            ),
            total_users=total_users,
            total_managers=total_managers,
            total_employees=total_employees,
        )

    @staticmethod
    def get_companies(
        db: Session,
    ) -> list[PlatformCompanyListItem]:
        companies = CompanyRepository.find_all(db)

        response: list[
            PlatformCompanyListItem
        ] = []

        for company in companies:
            response.append(
                PlatformCompanyListItem(
                    id=company.id,
                    code=company.code,
                    name=company.name,
                    is_active=company.is_active,
                    user_count=(
                        CompanyRepository.count_users(
                            db,
                            company.id,
                        )
                    ),
                    manager_count=(
                        CompanyRepository.count_managers(
                            db,
                            company.id,
                        )
                    ),
                    employee_count=(
                        CompanyRepository.count_employees(
                            db,
                            company.id,
                        )
                    ),
                    created_at=company.created_at,
                )
            )

        return response

    @staticmethod
    def create_company_with_admin(
        db: Session,
        request: CompanyWithAdminCreate,
    ) -> CompanyCreationResponse:
        normalized_name = (
            request.name
            .strip()
        )

        normalized_code = (
            request.code
            .strip()
            .upper()
        )

        normalized_username = (
            request.admin.username
            .strip()
            .lower()
        )

        normalized_tax_number = (
            request.tax_number.strip()
            if request.tax_number
            else None
        )

        normalized_address = (
            request.address.strip()
            if request.address
            else None
        )

        if (
            CompanyRepository.find_by_name(
                db,
                normalized_name,
            )
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A company with this name "
                    "already exists."
                ),
            )

        if (
            CompanyRepository.find_by_code(
                db,
                normalized_code,
            )
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A company with this code "
                    "already exists."
                ),
            )

        if (
            normalized_tax_number
            and CompanyRepository.find_by_tax_number(
                db,
                normalized_tax_number,
            )
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A company with this tax number "
                    "already exists."
                ),
            )

        if (
            UserRepository.find_by_username(
                db,
                normalized_username,
            )
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Administrator username "
                    "already exists."
                ),
            )

        company = Company(
            name=normalized_name,
            code=normalized_code,
            tax_number=normalized_tax_number,
            address=normalized_address,
            is_active=True,
        )

        try:
            db.add(company)
            db.flush()

            admin_user = User(
                company_id=company.id,
                username=normalized_username,
                password=hash_password(
                    request.admin.temporary_password
                ),
                role=UserRole.YONETICI.value,
                is_active=True,
                must_change_password=True,
            )

            db.add(admin_user)
            db.flush()

            db.commit()

            db.refresh(company)
            db.refresh(admin_user)

            return CompanyCreationResponse(
                company_id=company.id,
                company_name=company.name,
                company_code=company.code,
                admin_user_id=admin_user.id,
                admin_username=admin_user.username,
                must_change_password=(
                    admin_user.must_change_password
                ),
                message=(
                    "Company and initial administrator "
                    "were created successfully."
                ),
            )

        except IntegrityError as exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Company or administrator "
                    "information already exists."
                ),
            ) from exception

        except HTTPException:
            db.rollback()
            raise

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Company and administrator "
                    "could not be created."
                ),
            ) from exception

    @staticmethod
    def suspend_company(
        db: Session,
        company_id: int,
        request: CompanySuspendRequest,
    ) -> Company:
        company = CompanyRepository.find_by_id(
            db,
            company_id,
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company could not be found.",
            )

        company.is_active = False
        company.suspended_at = datetime.now(
            timezone.utc
        )
        company.suspension_reason = (
            request.reason.strip()
        )

        try:
            db.commit()
            db.refresh(company)

            return company

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail="Company could not be suspended.",
            ) from exception

    @staticmethod
    def activate_company(
        db: Session,
        company_id: int,
    ) -> Company:
        company = CompanyRepository.find_by_id(
            db,
            company_id,
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company could not be found.",
            )

        company.is_active = True
        company.suspended_at = None
        company.suspension_reason = None

        try:
            db.commit()
            db.refresh(company)

            return company

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail="Company could not be activated.",
            ) from exception
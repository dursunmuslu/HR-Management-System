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
from app.schemas.company_schema import (
    CompanyUpdate,
)


class CompanyService:

    @staticmethod
    def get_my_company(
        db: Session,
        current_user: User,
    ) -> Company:
        company_id = (
            CompanyService
            ._require_company_id(current_user)
        )

        company = CompanyRepository.find_by_id(
            db=db,
            company_id=company_id,
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company could not be found.",
            )

        return company

    @staticmethod
    def update_my_company(
        db: Session,
        request: CompanyUpdate,
        current_user: User,
    ) -> Company:
        company = CompanyService.get_my_company(
            db=db,
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
                update_data["name"]
                .strip()
            )

            existing_company = (
                CompanyRepository.find_by_name(
                    db=db,
                    name=normalized_name,
                )
            )

            if (
                existing_company is not None
                and existing_company.id
                != company.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A company with this name "
                        "already exists."
                    ),
                )

            update_data["name"] = (
                normalized_name
            )

        if "tax_number" in update_data:
            tax_number_value = (
                update_data["tax_number"]
            )

            normalized_tax_number = (
                tax_number_value.strip()
                if tax_number_value
                else None
            )

            if normalized_tax_number:
                existing_company = (
                    CompanyRepository
                    .find_by_tax_number(
                        db=db,
                        tax_number=(
                            normalized_tax_number
                        ),
                    )
                )

                if (
                    existing_company is not None
                    and existing_company.id
                    != company.id
                ):
                    raise HTTPException(
                        status_code=(
                            status.HTTP_409_CONFLICT
                        ),
                        detail=(
                            "A company with this tax "
                            "number already exists."
                        ),
                    )

            update_data["tax_number"] = (
                normalized_tax_number
            )

        if "address" in update_data:
            address_value = (
                update_data["address"]
            )

            normalized_address = (
                address_value.strip()
                if address_value
                else None
            )

            update_data["address"] = (
                normalized_address
            )

        for field_name, field_value in (
            update_data.items()
        ):
            setattr(
                company,
                field_name,
                field_value,
            )

        try:
            return CompanyRepository.save(
                db=db,
                company=company,
            )

        except IntegrityError as exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Company name or tax number "
                    "already exists."
                ),
            ) from exception

        except HTTPException:
            db.rollback()
            raise

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status
                    .HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Company information could not "
                    "be updated."
                ),
            ) from exception

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
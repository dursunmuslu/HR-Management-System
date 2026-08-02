from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.company import Company
from app.repositories.company_repository import (
    CompanyRepository,
)
from app.schemas.company_schema import (
    CompanyCreate,
    CompanyUpdate,
)


class CompanyService:

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Company]:
        return CompanyRepository.find_all(db)

    @staticmethod
    def get_by_id(
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

        return company

    @staticmethod
    def create(
        db: Session,
        request: CompanyCreate,
    ) -> Company:
        normalized_name = request.name.strip()

        existing_company = (
            CompanyRepository.find_by_name(
                db,
                normalized_name,
            )
        )

        if existing_company is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A company with this name already exists.",
            )

        company = Company(
            name=normalized_name,
            tax_number=(
                request.tax_number.strip()
                if request.tax_number
                else None
            ),
            address=(
                request.address.strip()
                if request.address
                else None
            ),
        )

        return CompanyRepository.save(
            db,
            company,
        )

    @staticmethod
    def update(
        db: Session,
        company_id: int,
        request: CompanyUpdate,
    ) -> Company:
        company = CompanyService.get_by_id(
            db,
            company_id,
        )

        update_data = request.model_dump(
            exclude_unset=True,
        )

        if "name" in update_data:
            normalized_name = update_data["name"].strip()

            existing_company = (
                CompanyRepository.find_by_name(
                    db,
                    normalized_name,
                )
            )

            if (
                existing_company is not None
                and existing_company.id != company.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A company with this name "
                        "already exists."
                    ),
                )

            update_data["name"] = normalized_name

        for field_name in [
            "tax_number",
            "address",
        ]:
            if (
                field_name in update_data
                and update_data[field_name] is not None
            ):
                update_data[field_name] = (
                    update_data[field_name].strip()
                )

        for field_name, field_value in update_data.items():
            setattr(
                company,
                field_name,
                field_value,
            )

        return CompanyRepository.save(
            db,
            company,
        )

    @staticmethod
    def delete(
        db: Session,
        company_id: int,
    ) -> None:
        company = CompanyService.get_by_id(
            db,
            company_id,
        )

        CompanyRepository.delete(
            db,
            company,
        )
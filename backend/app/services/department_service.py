from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.department import Department
from app.repositories.company_repository import (
    CompanyRepository,
)
from app.repositories.department_repository import (
    DepartmentRepository,
)
from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
)


class DepartmentService:

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Department]:
        return DepartmentRepository.find_all(db)

    @staticmethod
    def get_by_company(
        db: Session,
        company_id: int,
    ) -> list[Department]:
        company = CompanyRepository.find_by_id(
            db,
            company_id,
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company could not be found.",
            )

        return DepartmentRepository.find_by_company_id(
            db,
            company_id,
        )

    @staticmethod
    def get_by_id(
        db: Session,
        department_id: int,
    ) -> Department:
        department = DepartmentRepository.find_by_id(
            db,
            department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department could not be found.",
            )

        return department

    @staticmethod
    def create(
        db: Session,
        request: DepartmentCreate,
    ) -> Department:
        company = CompanyRepository.find_by_id(
            db,
            request.company_id,
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company could not be found.",
            )

        normalized_name = request.name.strip()

        existing_department = (
            DepartmentRepository
            .find_by_company_and_name(
                db,
                request.company_id,
                normalized_name,
            )
        )

        if existing_department is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A department with this name "
                    "already exists in the company."
                ),
            )

        department = Department(
            company_id=request.company_id,
            name=normalized_name,
            description=(
                request.description.strip()
                if request.description
                else None
            ),
        )

        return DepartmentRepository.save(
            db,
            department,
        )

    @staticmethod
    def update(
        db: Session,
        department_id: int,
        request: DepartmentUpdate,
    ) -> Department:
        department = DepartmentService.get_by_id(
            db,
            department_id,
        )

        update_data = request.model_dump(
            exclude_unset=True,
        )

        if "name" in update_data:
            normalized_name = update_data["name"].strip()

            existing_department = (
                DepartmentRepository
                .find_by_company_and_name(
                    db,
                    department.company_id,
                    normalized_name,
                )
            )

            if (
                existing_department is not None
                and existing_department.id
                != department.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A department with this name "
                        "already exists in the company."
                    ),
                )

            update_data["name"] = normalized_name

        if (
            "description" in update_data
            and update_data["description"] is not None
        ):
            update_data["description"] = (
                update_data["description"].strip()
            )

        for field_name, field_value in update_data.items():
            setattr(
                department,
                field_name,
                field_value,
            )

        return DepartmentRepository.save(
            db,
            department,
        )

    @staticmethod
    def delete(
        db: Session,
        department_id: int,
    ) -> None:
        department = DepartmentService.get_by_id(
            db,
            department_id,
        )

        DepartmentRepository.delete(
            db,
            department,
        )
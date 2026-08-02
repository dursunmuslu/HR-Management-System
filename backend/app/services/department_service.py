from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.user import User
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
        current_user: User,
    ) -> list[Department]:
        company_id = (
            DepartmentService
            ._require_company_id(current_user)
        )

        return (
            DepartmentRepository
            .find_all_by_company(
                db=db,
                company_id=company_id,
            )
        )

    @staticmethod
    def get_by_id(
        db: Session,
        department_id: int,
        current_user: User,
    ) -> Department:
        company_id = (
            DepartmentService
            ._require_company_id(current_user)
        )

        department = (
            DepartmentRepository
            .find_by_id_and_company(
                db=db,
                department_id=department_id,
                company_id=company_id,
            )
        )

        if department is None:
            # Başka şirkette bu ID'nin bulunduğunu
            # açıklamamak için 404 döndürülür.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department could not be found.",
            )

        return department

    @staticmethod
    def create(
        db: Session,
        request: DepartmentCreate,
        current_user: User,
    ) -> Department:
        company_id = (
            DepartmentService
            ._require_company_id(current_user)
        )

        normalized_name = (
            request.name
            .strip()
        )

        normalized_description = (
            request.description.strip()
            if request.description
            else None
        )

        existing_department = (
            DepartmentRepository
            .find_by_company_and_name(
                db=db,
                company_id=company_id,
                name=normalized_name,
            )
        )

        if existing_department is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A department with this name "
                    "already exists in your company."
                ),
            )

        department = Department(
            company_id=company_id,
            name=normalized_name,
            description=normalized_description,
            is_active=True,
        )

        return DepartmentRepository.save(
            db=db,
            department=department,
        )

    @staticmethod
    def update(
        db: Session,
        department_id: int,
        request: DepartmentUpdate,
        current_user: User,
    ) -> Department:
        company_id = (
            DepartmentService
            ._require_company_id(current_user)
        )

        department = (
            DepartmentService.get_by_id(
                db=db,
                department_id=department_id,
                current_user=current_user,
            )
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
                update_data["name"].strip()
            )

            existing_department = (
                DepartmentRepository
                .find_by_company_and_name(
                    db=db,
                    company_id=company_id,
                    name=normalized_name,
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
                        "already exists in your company."
                    ),
                )

            update_data["name"] = (
                normalized_name
            )

        if (
            "description" in update_data
            and update_data["description"] is not None
        ):
            description = (
                update_data["description"].strip()
            )

            update_data["description"] = (
                description or None
            )

        for field_name, field_value in (
            update_data.items()
        ):
            setattr(
                department,
                field_name,
                field_value,
            )

        return DepartmentRepository.save(
            db=db,
            department=department,
        )

    @staticmethod
    def deactivate(
        db: Session,
        department_id: int,
        current_user: User,
    ) -> Department:
        department = (
            DepartmentService.get_by_id(
                db=db,
                department_id=department_id,
                current_user=current_user,
            )
        )

        if not department.is_active:
            return department

        department.is_active = False

        # Departman pasife alındığında
        # altındaki takımlar da pasife alınır.
        for team in department.teams:
            team.is_active = False

        return DepartmentRepository.save(
            db=db,
            department=department,
        )

    @staticmethod
    def activate(
        db: Session,
        department_id: int,
        current_user: User,
    ) -> Department:
        department = (
            DepartmentService.get_by_id(
                db=db,
                department_id=department_id,
                current_user=current_user,
            )
        )

        if department.is_active:
            return department

        department.is_active = True

        return DepartmentRepository.save(
            db=db,
            department=department,
        )

    @staticmethod
    def delete(
        db: Session,
        department_id: int,
        current_user: User,
    ) -> None:
        department = (
            DepartmentService.get_by_id(
                db=db,
                department_id=department_id,
                current_user=current_user,
            )
        )

        has_employees = any(
            team.employees
            for team in department.teams
        )

        if has_employees:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A department containing employees "
                    "cannot be deleted. Deactivate it instead."
                ),
            )

        DepartmentRepository.delete(
            db=db,
            department=department,
        )

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
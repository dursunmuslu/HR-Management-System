from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.user import User
from app.repositories.employee_repository import (
    EmployeeRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.employee_schema import (
    EmployeeCreate,
    EmployeeCreateWithUser,
    EmployeeUpdate,
    LeaveBalanceResponse,
)
from app.security.password import hash_password
from app.security.user_role import UserRole


class EmployeeService:

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Employee]:
        return EmployeeRepository.find_all(db)

    @staticmethod
    def get_by_id(
        db: Session,
        employee_id: int,
    ) -> Employee:
        employee = EmployeeRepository.find_by_id(
            db,
            employee_id,
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee could not be found.",
            )

        return employee

    @staticmethod
    def get_my_profile(
        db: Session,
        current_user: User,
    ) -> Employee:
        employee = EmployeeRepository.find_by_user_id(
            db,
            current_user.id,
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Employee profile could not be found "
                    "for the current user."
                ),
            )

        return employee

    @staticmethod
    def get_my_leave_balance(
        db: Session,
        current_user: User,
    ) -> LeaveBalanceResponse:
        employee = EmployeeService.get_my_profile(
            db,
            current_user,
        )

        return LeaveBalanceResponse(
            employee_id=employee.id,
            employee_number=employee.employee_number,
            first_name=employee.first_name,
            last_name=employee.last_name,
            remaining_annual_leave=(
                employee.remaining_annual_leave
            ),
        )

    @staticmethod
    def create_with_user(
        db: Session,
        request: EmployeeCreateWithUser,
    ) -> Employee:
        """
        Kullanıcı hesabını ve personel profilini
        aynı transaction içerisinde oluşturur.
        """

        normalized_username = (
            request.username
            .strip()
            .lower()
        )

        normalized_tc_no = (
            request.tc_no
            .strip()
        )

        normalized_employee_number = (
            request.employee_number
            .strip()
        )

        normalized_email = (
            str(request.email)
            .strip()
            .lower()
        )

        normalized_phone = (
            request.phone
            .strip()
        )

        existing_user = UserRepository.find_by_username(
            db,
            normalized_username,
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            )

        existing_tc = EmployeeRepository.find_by_tc_no(
            db,
            normalized_tc_no,
        )

        if existing_tc is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An employee with this identification "
                    "number already exists."
                ),
            )

        existing_employee_number = (
            EmployeeRepository.find_by_employee_number(
                db,
                normalized_employee_number,
            )
        )

        if existing_employee_number is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An employee with this employee "
                    "number already exists."
                ),
            )

        existing_email = EmployeeRepository.find_by_email(
            db,
            normalized_email,
        )

        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An employee with this email "
                    "already exists."
                ),
            )

        user = User(
            username=normalized_username,
            password=hash_password(
                request.password
            ),
            role=UserRole.PERSONEL.value,
        )

        try:
            db.add(user)
            db.flush()

            employee = Employee(
                user_id=user.id,
                first_name=request.first_name.strip(),
                last_name=request.last_name.strip(),
                tc_no=normalized_tc_no,
                employee_number=(
                    normalized_employee_number
                ),
                department=request.department.strip(),
                position=request.position.strip(),
                phone=normalized_phone,
                email=normalized_email,
                hire_date=request.hire_date,
                remaining_annual_leave=(
                    request.remaining_annual_leave
                ),
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)

            created_employee = (
                EmployeeRepository.find_by_id(
                    db,
                    employee.id,
                )
            )

            if created_employee is None:
                raise HTTPException(
                    status_code=(
                        status.HTTP_500_INTERNAL_SERVER_ERROR
                    ),
                    detail=(
                        "Created employee could not be loaded."
                    ),
                )

            return created_employee

        except IntegrityError as exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Username, identification number, "
                    "employee number or email already exists."
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
                    "Employee and user account could not "
                    "be created."
                ),
            ) from exception

    @staticmethod
    def create(
        db: Session,
        request: EmployeeCreate,
    ) -> Employee:
        user = UserRepository.find_by_id(
            db,
            request.user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User could not be found.",
            )

        existing_user_employee = (
            EmployeeRepository.find_by_user_id(
                db,
                request.user_id,
            )
        )

        if existing_user_employee is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An employee profile already exists "
                    "for this user."
                ),
            )

        normalized_tc_no = (
            request.tc_no.strip()
        )

        normalized_employee_number = (
            request.employee_number.strip()
        )

        normalized_email = (
            str(request.email)
            .strip()
            .lower()
        )

        if (
            EmployeeRepository.find_by_tc_no(
                db,
                normalized_tc_no,
            )
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An employee with this identification "
                    "number already exists."
                ),
            )

        if (
            EmployeeRepository.find_by_employee_number(
                db,
                normalized_employee_number,
            )
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An employee with this employee "
                    "number already exists."
                ),
            )

        if (
            EmployeeRepository.find_by_email(
                db,
                normalized_email,
            )
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An employee with this email "
                    "already exists."
                ),
            )

        employee = Employee(
            user_id=request.user_id,
            first_name=request.first_name.strip(),
            last_name=request.last_name.strip(),
            tc_no=normalized_tc_no,
            employee_number=normalized_employee_number,
            department=request.department.strip(),
            position=request.position.strip(),
            phone=request.phone.strip(),
            email=normalized_email,
            hire_date=request.hire_date,
            remaining_annual_leave=(
                request.remaining_annual_leave
            ),
        )

        created_employee = (
            EmployeeRepository.create(
                db,
                employee,
            )
        )

        loaded_employee = (
            EmployeeRepository.find_by_id(
                db,
                created_employee.id,
            )
        )

        if loaded_employee is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Created employee could not be loaded."
                ),
            )

        return loaded_employee

    @staticmethod
    def update(
        db: Session,
        employee_id: int,
        request: EmployeeUpdate,
    ) -> Employee:
        employee = EmployeeService.get_by_id(
            db,
            employee_id,
        )

        update_data = request.model_dump(
            exclude_unset=True,
        )

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "At least one field must be provided "
                    "for update."
                ),
            )

        if "tc_no" in update_data:
            normalized_tc_no = (
                update_data["tc_no"].strip()
            )

            existing_employee = (
                EmployeeRepository.find_by_tc_no(
                    db,
                    normalized_tc_no,
                )
            )

            if (
                existing_employee is not None
                and existing_employee.id != employee.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "An employee with this "
                        "identification number already "
                        "exists."
                    ),
                )

            update_data["tc_no"] = (
                normalized_tc_no
            )

        if "employee_number" in update_data:
            normalized_employee_number = (
                update_data[
                    "employee_number"
                ].strip()
            )

            existing_employee = (
                EmployeeRepository
                .find_by_employee_number(
                    db,
                    normalized_employee_number,
                )
            )

            if (
                existing_employee is not None
                and existing_employee.id != employee.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "An employee with this employee "
                        "number already exists."
                    ),
                )

            update_data["employee_number"] = (
                normalized_employee_number
            )

        if "email" in update_data:
            normalized_email = (
                str(update_data["email"])
                .strip()
                .lower()
            )

            existing_employee = (
                EmployeeRepository.find_by_email(
                    db,
                    normalized_email,
                )
            )

            if (
                existing_employee is not None
                and existing_employee.id != employee.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "An employee with this email "
                        "already exists."
                    ),
                )

            update_data["email"] = (
                normalized_email
            )

        string_fields = [
            "first_name",
            "last_name",
            "department",
            "position",
            "phone",
        ]

        for field_name in string_fields:
            if field_name in update_data:
                update_data[field_name] = (
                    update_data[field_name].strip()
                )

        for field_name, field_value in (
            update_data.items()
        ):
            setattr(
                employee,
                field_name,
                field_value,
            )

        saved_employee = (
            EmployeeRepository.save(
                db,
                employee,
            )
        )

        loaded_employee = (
            EmployeeRepository.find_by_id(
                db,
                saved_employee.id,
            )
        )

        if loaded_employee is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Updated employee could not be loaded."
                ),
            )

        return loaded_employee

    @staticmethod
    def delete(
        db: Session,
        employee_id: int,
    ) -> None:
        employee = EmployeeService.get_by_id(
            db,
            employee_id,
        )

        try:
            user = employee.user

            if user is not None:
                db.delete(user)
            else:
                db.delete(employee)

            db.commit()

        except Exception as exception:
            db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Employee could not be deleted."
                ),
            ) from exception
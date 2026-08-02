from datetime import date

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.user import User
from app.repositories.employee_repository import (
    EmployeeRepository,
)
from app.repositories.leave_repository import (
    LeaveRepository,
)
from app.schemas.leave_schema import (
    LeaveApprove,
    LeaveCreate,
    LeaveReject,
)
from app.security.leave_status import LeaveStatus
from app.security.leave_type import LeaveType


class LeaveService:

    @staticmethod
    def get_employee_profile(
        db: Session,
        current_user: User,
    ) -> Employee:
        employee = (
            EmployeeRepository.find_by_user_id(
                db=db,
                user_id=current_user.id,
            )
        )

        if (
            employee is None
            or employee.user is None
            or employee.user.company_id
            != current_user.company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Employee profile could not be found "
                    "for the current user."
                ),
            )

        return employee

    @staticmethod
    def calculate_number_of_days(
        start_date: date,
        end_date: date,
    ) -> int:
        return (
            end_date - start_date
        ).days + 1

    @staticmethod
    def create(
        db: Session,
        request: LeaveCreate,
        current_user: User,
    ) -> LeaveRequest:
        employee = (
            LeaveService.get_employee_profile(
                db=db,
                current_user=current_user,
            )
        )

        today = date.today()

        if request.start_date < today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Leave start date cannot be "
                    "earlier than today."
                ),
            )

        if request.end_date < request.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Leave end date cannot be earlier "
                    "than the start date."
                ),
            )

        number_of_days = (
            LeaveService.calculate_number_of_days(
                request.start_date,
                request.end_date,
            )
        )

        overlapping_leave = (
            LeaveRepository.find_overlapping_leave(
                db=db,
                employee_id=employee.id,
                start_date=request.start_date,
                end_date=request.end_date,
            )
        )

        if overlapping_leave is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "There is already a pending or "
                    "approved leave request for the "
                    "selected dates."
                ),
            )

        if (
            request.leave_type
            == LeaveType.YILLIK_IZIN
            and number_of_days
            > employee.remaining_annual_leave
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Annual leave balance is insufficient."
                ),
            )

        description = (
            request.description.strip()
            if request.description
            else None
        )

        leave_request = LeaveRequest(
            employee_id=employee.id,
            leave_type=request.leave_type.value,
            start_date=request.start_date,
            end_date=request.end_date,
            number_of_days=number_of_days,
            description=description or None,
            status=LeaveStatus.PENDING.value,
        )

        return LeaveRepository.create(
            db=db,
            leave_request=leave_request,
        )

    @staticmethod
    def get_my_leaves(
        db: Session,
        current_user: User,
    ) -> list[LeaveRequest]:
        employee = (
            LeaveService.get_employee_profile(
                db=db,
                current_user=current_user,
            )
        )

        return LeaveRepository.find_by_employee_id(
            db=db,
            employee_id=employee.id,
        )

    @staticmethod
    def get_my_leave_by_id(
        db: Session,
        leave_id: int,
        current_user: User,
    ) -> LeaveRequest:
        employee = (
            LeaveService.get_employee_profile(
                db=db,
                current_user=current_user,
            )
        )

        leave_request = (
            LeaveRepository
            .find_employee_leave_by_id(
                db=db,
                employee_id=employee.id,
                leave_id=leave_id,
            )
        )

        if leave_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request could not be found.",
            )

        return leave_request

    @staticmethod
    def cancel(
        db: Session,
        leave_id: int,
        current_user: User,
    ) -> LeaveRequest:
        leave_request = (
            LeaveService.get_my_leave_by_id(
                db=db,
                leave_id=leave_id,
                current_user=current_user,
            )
        )

        if (
            leave_request.status
            != LeaveStatus.PENDING.value
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Only pending leave requests "
                    "can be cancelled."
                ),
            )

        leave_request.status = (
            LeaveStatus.CANCELLED.value
        )

        return LeaveRepository.save(
            db=db,
            leave_request=leave_request,
        )

    @staticmethod
    def get_all(
        db: Session,
        current_user: User,
    ) -> list[LeaveRequest]:
        company_id = (
            LeaveService
            ._require_company_id(current_user)
        )

        return (
            LeaveRepository
            .find_all_by_company(
                db=db,
                company_id=company_id,
            )
        )

    @staticmethod
    def get_pending(
        db: Session,
        current_user: User,
    ) -> list[LeaveRequest]:
        company_id = (
            LeaveService
            ._require_company_id(current_user)
        )

        return (
            LeaveRepository
            .find_pending_by_company(
                db=db,
                company_id=company_id,
            )
        )

    @staticmethod
    def get_by_id(
        db: Session,
        leave_id: int,
        current_user: User,
    ) -> LeaveRequest:
        company_id = (
            LeaveService
            ._require_company_id(current_user)
        )

        leave_request = (
            LeaveRepository.find_by_id_and_company(
                db=db,
                leave_id=leave_id,
                company_id=company_id,
            )
        )

        if leave_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request could not be found.",
            )

        return leave_request

    @staticmethod
    def approve(
        db: Session,
        leave_id: int,
        request: LeaveApprove,
        current_user: User,
    ) -> LeaveRequest:
        leave_request = LeaveService.get_by_id(
            db=db,
            leave_id=leave_id,
            current_user=current_user,
        )

        if (
            leave_request.status
            != LeaveStatus.PENDING.value
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Only pending leave requests "
                    "can be approved."
                ),
            )

        employee = leave_request.employee

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Employee belonging to the leave "
                    "request could not be found."
                ),
            )

        leave_type_value = (
            leave_request.leave_type.value
            if hasattr(
                leave_request.leave_type,
                "value",
            )
            else leave_request.leave_type
        )

        if (
            leave_type_value
            == LeaveType.YILLIK_IZIN.value
        ):
            if (
                leave_request.number_of_days
                > employee.remaining_annual_leave
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Employee annual leave balance "
                        "is insufficient."
                    ),
                )

            employee.remaining_annual_leave -= (
                leave_request.number_of_days
            )

        manager_note = (
            request.manager_note.strip()
            if request.manager_note
            else None
        )

        leave_request.status = (
            LeaveStatus.APPROVED.value
        )

        leave_request.manager_note = (
            manager_note or None
        )

        return (
            LeaveRepository
            .approve_with_employee_balance(
                db=db,
                leave_request=leave_request,
            )
        )

    @staticmethod
    def reject(
        db: Session,
        leave_id: int,
        request: LeaveReject,
        current_user: User,
    ) -> LeaveRequest:
        leave_request = LeaveService.get_by_id(
            db=db,
            leave_id=leave_id,
            current_user=current_user,
        )

        if (
            leave_request.status
            != LeaveStatus.PENDING.value
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Only pending leave requests "
                    "can be rejected."
                ),
            )

        manager_note = (
            request.manager_note.strip()
        )

        if not manager_note:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager note cannot be empty.",
            )

        leave_request.status = (
            LeaveStatus.REJECTED.value
        )

        leave_request.manager_note = manager_note

        return LeaveRepository.save(
            db=db,
            leave_request=leave_request,
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
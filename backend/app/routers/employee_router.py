from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.employee_schema import (
    EmployeeCreate,
    EmployeeCreateWithUser,
    EmployeeProfileResponse,
    EmployeeResponse,
    EmployeeUpdate,
    LeaveBalanceResponse,
)
from app.security.auth_dependency import (
    get_current_user,
    require_manager,
)
from app.services.employee_service import EmployeeService


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.get(
    "/me/leave-balance",
    response_model=LeaveBalanceResponse,
)
def get_my_leave_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return EmployeeService.get_my_leave_balance(
        db,
        current_user,
    )


@router.get(
    "/me",
    response_model=EmployeeProfileResponse,
)
def get_my_employee_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return EmployeeService.get_my_profile(
        db,
        current_user,
    )


@router.post(
    "/create-with-user",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee_with_user(
    request: EmployeeCreateWithUser,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return EmployeeService.create_with_user(
        db,
        request,
    )


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    request: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return EmployeeService.create(
        db,
        request,
    )


@router.get(
    "",
    response_model=list[EmployeeResponse],
)
def get_all_employees(
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return EmployeeService.get_all(db)


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return EmployeeService.get_by_id(
        db,
        employee_id,
    )


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def update_employee(
    employee_id: int,
    request: EmployeeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    return EmployeeService.update(
        db,
        employee_id,
        request,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    EmployeeService.delete(
        db,
        employee_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
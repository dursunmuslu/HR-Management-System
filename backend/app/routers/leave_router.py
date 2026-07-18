from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.leave_schema import (
    LeaveApprove,
    LeaveCreate,
    LeaveDetailResponse,
    LeaveReject,
    LeaveResponse
)
from app.security.auth_dependency import (
    get_current_user,
    require_manager
)
from app.services.leave_service import LeaveService


router = APIRouter(
    prefix="/leave",
    tags=["Leave Management"]
)


@router.post(
    "",
    response_model=LeaveResponse,
    status_code=status.HTTP_201_CREATED
)
def create_leave_request(
    request: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return LeaveService.create(
        db,
        request,
        current_user
    )


@router.get(
    "/my-leaves",
    response_model=list[LeaveResponse]
)
def get_my_leave_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return LeaveService.get_my_leaves(
        db,
        current_user
    )


@router.get(
    "/my-leaves/{leave_id}",
    response_model=LeaveResponse
)
def get_my_leave_request(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return LeaveService.get_my_leave_by_id(
        db,
        leave_id,
        current_user
    )


@router.delete(
    "/{leave_id}",
    response_model=LeaveResponse
)
def cancel_leave_request(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return LeaveService.cancel(
        db,
        leave_id,
        current_user
    )


@router.get(
    "",
    response_model=list[LeaveDetailResponse]
)
def get_all_leave_requests(
    db: Session = Depends(get_db),
    _: User = Depends(require_manager)
):
    return LeaveService.get_all(db)


@router.get(
    "/pending",
    response_model=list[LeaveDetailResponse]
)
def get_pending_leave_requests(
    db: Session = Depends(get_db),
    _: User = Depends(require_manager)
):
    return LeaveService.get_pending(db)


@router.get(
    "/{leave_id}",
    response_model=LeaveDetailResponse
)
def get_leave_request(
    leave_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager)
):
    return LeaveService.get_by_id(
        db,
        leave_id
    )


@router.put(
    "/{leave_id}/approve",
    response_model=LeaveDetailResponse
)
def approve_leave_request(
    leave_id: int,
    request: LeaveApprove,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager)
):
    return LeaveService.approve(
        db,
        leave_id,
        request
    )


@router.put(
    "/{leave_id}/reject",
    response_model=LeaveDetailResponse
)
def reject_leave_request(
    leave_id: int,
    request: LeaveReject,
    db: Session = Depends(get_db),
    _: User = Depends(require_manager)
):
    return LeaveService.reject(
        db,
        leave_id,
        request
    )
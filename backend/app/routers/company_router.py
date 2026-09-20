from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.company import Company
from app.models.user import User
from app.security.auth_dependency import get_current_user, require_manager_or_owner

router = APIRouter(prefix="/companies", tags=["Companies"])


class CompanyModuleSettingsSchema(BaseModel):
    is_announcements_enabled: bool = True
    is_quizzes_enabled: bool = True
    is_shifts_enabled: bool = True
    is_leaves_enabled: bool = True
    is_timesheets_enabled: bool = True


@router.get("/my-settings")
def get_my_company_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.company_id:
        return CompanyModuleSettingsSchema()

    comp = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not comp:
        return CompanyModuleSettingsSchema()

    return {
        "is_announcements_enabled": getattr(comp, "is_announcements_enabled", True),
        "is_quizzes_enabled": getattr(comp, "is_quizzes_enabled", True),
        "is_shifts_enabled": getattr(comp, "is_shifts_enabled", True),
        "is_leaves_enabled": getattr(comp, "is_leaves_enabled", True),
        "is_timesheets_enabled": getattr(comp, "is_timesheets_enabled", True),
    }


@router.put("/my-settings")
def update_my_company_settings(
    payload: CompanyModuleSettingsSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_owner),
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Kullanıcıya bağlı şirket bulunamadı.")

    comp = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Şirket bulunamadı.")

    comp.is_announcements_enabled = payload.is_announcements_enabled
    comp.is_quizzes_enabled = payload.is_quizzes_enabled
    comp.is_shifts_enabled = payload.is_shifts_enabled
    comp.is_leaves_enabled = payload.is_leaves_enabled
    comp.is_timesheets_enabled = payload.is_timesheets_enabled

    db.commit()
    db.refresh(comp)

    return {
        "is_announcements_enabled": comp.is_announcements_enabled,
        "is_quizzes_enabled": comp.is_quizzes_enabled,
        "is_shifts_enabled": comp.is_shifts_enabled,
        "is_leaves_enabled": comp.is_leaves_enabled,
        "is_timesheets_enabled": comp.is_timesheets_enabled,
    }
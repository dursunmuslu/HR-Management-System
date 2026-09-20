from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.announcement import Announcement
from app.models.user import User
from app.security.auth_dependency import get_current_user, require_manager_or_owner
from app.security.user_role import UserRole

router = APIRouter(prefix="/announcements", tags=["Announcements"])

class AnnouncementCreate(BaseModel):
    title: str
    category: Optional[str] = "Genel"
    content: str
    is_pinned: Optional[bool] = False

@router.get("")
def list_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Announcement)
    if current_user.company_id:
        query = query.filter(Announcement.company_id == current_user.company_id)

    # Önce sabitlenenler, sonra en yeni eklenenler
    announcements = query.order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "category": a.category,
            "content": a.content,
            "author": a.author_name,
            "isPinned": a.is_pinned,
            "date": a.created_at.strftime("%d.%m.%Y %H:%M") if a.created_at else "Bugün"
        }
        for a in announcements
    ]

@router.post("")
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_owner)
):
    if not current_user.company_id and current_user.role != UserRole.PLATFORM_OWNER.value:
        raise HTTPException(status_code=400, detail="Bir şirkete bağlı değilsiniz.")

    company_id = current_user.company_id or 1

    announcement = Announcement(
        company_id=company_id,
        title=data.title,
        category=data.category,
        content=data.content,
        author_name=current_user.username,
        is_pinned=data.is_pinned
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement

@router.put("/{announcement_id}/toggle-pin")
def toggle_pin(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_owner)
):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Duyuru bulunamadı.")

    announcement.is_pinned = not announcement.is_pinned
    db.commit()
    return {"status": "success", "isPinned": announcement.is_pinned}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database.session import get_db
from backend.models.user import User
from backend.models.settings import Settings as SettingsModel
from backend.api.v1.routes.deps import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    role: str
    storage_usage_bytes: float
    
    class Config:
        from_attributes = True

class SettingsSchema(BaseModel):
    theme: str
    language: str
    email_notifications: bool
    auto_save: bool
    llm_model: str
    
    class Config:
        from_attributes = True

class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    email_notifications: Optional[bool] = None
    auto_save: Optional[bool] = None
    llm_model: Optional[str] = None

@router.get("/me", response_model=UserProfile)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/settings", response_model=SettingsSchema)
def get_user_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings = db.query(SettingsModel).filter(SettingsModel.user_id == current_user.id).first()
    if not settings:
        settings = SettingsModel(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/me/settings", response_model=SettingsSchema)
def update_user_settings(
    settings_update: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(SettingsModel).filter(SettingsModel.user_id == current_user.id).first()
    if not settings:
        settings = SettingsModel(user_id=current_user.id)
        db.add(settings)
    
    update_data = settings_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
        
    db.commit()
    db.refresh(settings)
    return settings

from typing import List
from sqlalchemy.orm import Session
from backend.repositories.base import BaseRepository
from backend.models.resume import Resume

class ResumeRepository(BaseRepository[Resume]):
    def get_by_user_id(self, db: Session, user_id: int) -> List[Resume]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

resume_repository = ResumeRepository(Resume)

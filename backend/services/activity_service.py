from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models.database import Activity, Lead


class ActivityService:
    @staticmethod
    def get_activities_for_lead(db: Session, lead_id: int):
        return db.query(Activity).filter(Activity.lead_id == lead_id).all()
    
    @staticmethod
    def create_activity(db: Session, lead_id: int, activity_type: str, notes: str = None):
        activity = Activity(lead_id=lead_id, activity_type=activity_type, notes=notes)
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def get_recent_activities(db: Session, days: int = 7, limit: int = 50):
        cutoff_date = date.today() - timedelta(days=days)
        return db.query(Activity).filter(
            Activity.created_at >= cutoff_date
        ).order_by(Activity.created_at.desc()).limit(limit).all()
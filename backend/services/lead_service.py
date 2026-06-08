from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models.database import Lead, Activity


class LeadService:
    @staticmethod
    def get_lead_by_id(db: Session, lead_id: int):
        return db.query(Lead).filter(Lead.lead_id == lead_id).first()
    
    @staticmethod
    def get_leads_by_category(db: Session, category: str):
        return db.query(Lead).filter(Lead.category == category).all()
    
    @staticmethod
    def get_stale_leads(db: Session, days: int = 7):
        cutoff_date = date.today() - timedelta(days=days)
        return db.query(Lead).filter(
            Lead.last_contact_date.is_(None) | (Lead.last_contact_date < cutoff_date)
        ).all()
    
    @staticmethod
    def add_activity(db: Session, lead_id: int, activity_type: str, notes: str = None):
        activity = Activity(lead_id=lead_id, activity_type=activity_type, notes=notes)
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def update_lead_contact_date(db: Session, lead_id: int):
        lead = LeadService.get_lead_by_id(db, lead_id)
        if lead:
            lead.last_contact_date = date.today()
            db.commit()
            db.refresh(lead)
        return lead
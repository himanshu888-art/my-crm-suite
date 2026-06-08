from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import date, timedelta
import logging

from ..database.session import SessionLocal
from ..models.database import Lead, Task, TaskStatus
from llm.email_generator import generate_automation_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_stale_leads():
    logger.info("Running stale lead check...")
    
    db = SessionLocal()
    try:
        cutoff_date = date.today() - timedelta(days=7)
        
        stale_leads = db.query(Lead).filter(
            Lead.status.notin_(["closed_won", "closed_lost"]),
            (Lead.last_contact_date.is_(None) | (Lead.last_contact_date < cutoff_date))
        ).all()
        
        tasks_created = 0
        for lead in stale_leads:
            existing_task = db.query(Task).filter(
                Task.lead_id == lead.lead_id,
                Task.status == TaskStatus.PENDING.value,
                Task.task_type == "follow_up"
            ).first()
            
            if not existing_task:
                email_draft = generate_automation_email(
                    company=lead.company, lead_name=lead.name, context="follow_up"
                )
                
                task = Task(
                    lead_id=lead.lead_id, task_type="follow_up",
                    description=f"Follow up with {lead.company} - stale for 7+ days",
                    due_date=date.today(), status=TaskStatus.PENDING.value,
                    email_draft=email_draft
                )
                
                db.add(task)
                tasks_created += 1
                logger.info(f"Created follow-up task for {lead.company}")
        
        db.commit()
        logger.info(f"Stale lead check complete. Created {tasks_created} tasks.")
    
    except Exception as e:
        logger.error(f"Error in stale lead check: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        check_stale_leads,
        trigger=CronTrigger(hour=9, minute=0),
        id="stale_lead_checker",
        name="Check for stale leads daily",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - checking for stale leads daily at 9 AM")
    
    return scheduler
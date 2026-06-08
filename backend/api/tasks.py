from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date

from ..database.session import get_db
from ..models.database import Task, TaskStatus, Lead
from llm.email_generator import generate_automation_email


class TaskCreate(BaseModel):
    lead_id: int
    task_type: str
    description: str | None = None
    due_date: str | None = None

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/")
async def get_tasks(status: str = None, lead_id: int = None, 
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if lead_id:
        query = query.filter(Task.lead_id == lead_id)
    
    tasks = query.offset(skip).limit(limit).all()
    return {"tasks": tasks}


@router.get("/dashboard/daily")
async def get_daily_tasks(db: Session = Depends(get_db)):
    today = date.today()
    
    pending_tasks = db.query(Task).filter(
        Task.status == TaskStatus.PENDING.value, Task.due_date <= today
    ).all()
    
    overdue_tasks = db.query(Task).filter(
        Task.status == TaskStatus.PENDING.value, Task.due_date < today
    ).all()
    
    return {
        "today": today.isoformat(), "total_pending": len(pending_tasks),
        "overdue": len(overdue_tasks), "tasks": pending_tasks,
        "overdue_tasks": overdue_tasks
    }


@router.post("/")
async def create_task(request: TaskCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == request.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    email_draft = None
    if request.task_type == "follow_up":
        email_draft = generate_automation_email(
            company=lead.company, lead_name=lead.name, context="follow_up"
        )
    
    task = Task(
        lead_id=request.lead_id,
        task_type=request.task_type,
        description=request.description,
        due_date=date.fromisoformat(request.due_date) if request.due_date else date.today(),
        email_draft=email_draft
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return {"task": task, "email_draft": email_draft}


@router.put("/{task_id}")
async def update_task(task_id: int, status: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = status
    
    if status == TaskStatus.COMPLETED.value:
        lead = db.query(Lead).filter(Lead.lead_id == task.lead_id).first()
        if lead:
            lead.last_contact_date = date.today()
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
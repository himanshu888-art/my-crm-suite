from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
import csv
import io

from ..database.session import get_db
from ..models.database import Lead, LeadStatus
from llm.lead_scoring import score_lead, classify_lead


class LeadCreate(BaseModel):
    name: str
    company: str
    email: str
    phone: str | None = None
    industry: str | None = None
    employees: int | None = None
    revenue: int | None = None
    message: str | None = None

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("/")
async def get_leads(skip: int = 0, limit: int = 100, status: str = None, 
                   category: str = None, db: Session = Depends(get_db)):
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    if category:
        query = query.filter(Lead.category == category)
    
    leads = query.offset(skip).limit(limit).all()
    return {"leads": leads, "total": query.count()}


@router.get("/{lead_id}")
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/")
async def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    lead_data = lead_in.dict()
    score, reason = score_lead(lead_data)
    category = classify_lead(score)
    
    lead = Lead(
        name=lead_in.name,
        company=lead_in.company,
        email=lead_in.email,
        phone=lead_in.phone,
        industry=lead_in.industry,
        employees=lead_in.employees,
        revenue=lead_in.revenue,
        message=lead_in.message,
        status=LeadStatus.NEW.value,
        lead_score=score,
        category=category
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return {"lead": lead, "score": score, "category": category, "reason": reason}


@router.post("/upload-csv")
async def upload_leads_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(contents))
    
    leads_added = []
    for row in reader:
        lead_data = {
            "name": row.get("name"), "company": row.get("company"),
            "email": row.get("email"), "industry": row.get("industry"),
            "employees": int(row.get("employees", 0)),
            "message": row.get("message")
        }
        
        score, reason = score_lead(lead_data)
        category = classify_lead(score)
        
        lead = Lead(
            name=lead_data["name"], company=lead_data["company"],
            email=lead_data["email"], industry=lead_data["industry"],
            employees=lead_data["employees"], message=lead_data["message"],
            status=LeadStatus.NEW.value, lead_score=score, category=category
        )
        db.add(lead)
        leads_added.append(lead.company)
    
    db.commit()
    return {"message": f"Added {len(leads_added)} leads", "leads": leads_added}


@router.put("/{lead_id}")
async def update_lead(lead_id: int, status: str = None, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if status:
        lead.status = status
    
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    return {"message": "Lead deleted successfully"}


@router.get("/stats/summary")
async def get_lead_stats(db: Session = Depends(get_db)):
    total = db.query(Lead).count()
    hot = db.query(Lead).filter(Lead.category == "Hot").count()
    warm = db.query(Lead).filter(Lead.category == "Warm").count()
    cold = db.query(Lead).filter(Lead.category == "Cold").count()
    
    return {
        "total_leads": total, "hot_leads": hot, "warm_leads": warm,
        "cold_leads": cold,
        "hot_percentage": round((hot / total * 100) if total > 0 else 0, 2)
    }
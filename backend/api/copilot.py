from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta

from ..database.session import get_db
from ..models.database import Lead, Activity
from llm.copilot import generate_sql_query, summarize_response, generate_follow_up_email


class CopilotQuery(BaseModel):
    user_query: str


class EmailRequest(BaseModel):
    company: str
    lead_context: str | None = None
    email_type: str = "follow_up"


router = APIRouter(prefix="/copilot", tags=["CRM Copilot"])


@router.post("/query")
async def copilot_query(request: CopilotQuery, db: Session = Depends(get_db)):
    try:
        sql_query, explanation = generate_sql_query(request.user_query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {str(e)}")
    
    try:
        result = db.execute(text(sql_query))
        rows = result.mappings().all()
        data = [dict(row) for row in rows]
        summary = summarize_response(request.user_query, data)
        
        return {
            "user_query": request.user_query,
            "sql_query": sql_query,
            "explanation": explanation,
            "results": data,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")


@router.get("/leads/hot")
async def get_hot_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).filter(Lead.category == "Hot").order_by(Lead.lead_score.desc()).all()
    return {"hot_leads": leads}


@router.get("/leads/not-contacted/{days}")
async def get_leads_not_contacted(days: int, db: Session = Depends(get_db)):
    cutoff_date = date.today() - timedelta(days=days)
    leads = db.query(Lead).filter(
        Lead.last_contact_date.is_(None) | (Lead.last_contact_date < cutoff_date)
    ).all()
    return {"leads": leads, "days": days}


@router.post("/email/generate")
async def generate_email(request: EmailRequest, db: Session = Depends(get_db)):
    email_content = generate_follow_up_email(
        company=request.company,
        context=request.lead_context,
        email_type=request.email_type
    )
    return {
        "company": request.company,
        "email_type": request.email_type,
        "email_draft": email_content
    }


@router.get("/leads/{lead_id}/summary")
async def get_lead_summary(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    activities = db.query(Activity).filter(Activity.lead_id == lead_id).all()
    
    summary_text = f"""Lead Summary for {lead.company}
    ================================
    Contact: {lead.name} ({lead.email})
    Industry: {lead.industry}
    Employees: {lead.employees}
    Status: {lead.status}
    Score: {lead.lead_score}/100 ({lead.category})
    Recent Activities: {len(activities)}
    Last Contact: {lead.last_contact_date}"""
    
    return {"lead": lead, "activities_count": len(activities), "summary": summary_text}


@router.get("/recommendations")
async def get_task_recommendations(db: Session = Depends(get_db)):
    cutoff_date = date.today() - timedelta(days=3)
    
    hot_leads = db.query(Lead).filter(
        Lead.category == "Hot",
        (Lead.last_contact_date.is_(None) | (Lead.last_contact_date < cutoff_date))
    ).limit(5).all()
    
    recommendations = []
    for lead in hot_leads:
        recommendations.append({
            "lead_id": lead.lead_id, "company": lead.company,
            "priority": "High", "action": "Follow up immediately",
            "reason": f"Hot lead (score: {lead.lead_score}) not contacted recently"
        })
    
    return {"recommendations": recommendations}
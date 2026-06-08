import json
from .client import client, settings

SCORING_PROMPT = """
You are an AI lead scoring expert. Analyze the lead and assign a score from 0-100.

Lead Data:
- Company: {company}
- Industry: {industry}
- Employees: {employees}
- Message: {message}

Scoring Criteria:
- Company size (employees): 500+ = 30pts, 100-499 = 20pts, 50-99 = 10pts
- Industry fit (SaaS, Tech, Finance = 25pts)
- Buying intent in message (enterprise, solution, pricing = 30pts)
- Company name professionalism (15pts)

Return ONLY a JSON object:
{{"score": <integer 0-100>, "reason": "<brief explanation in 10 words>"}}
"""


def score_lead(lead_data: dict) -> tuple:
    prompt = SCORING_PROMPT.format(
        company=lead_data.get("company", "Unknown"),
        industry=lead_data.get("industry", "Unknown"),
        employees=lead_data.get("employees", 0),
        message=lead_data.get("message", "No message")
    )
    
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a lead scoring AI. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result["score"], result["reason"]
    
    except Exception as e:
        return rule_based_score(lead_data), "AI unavailable, using rule-based scoring"


def rule_based_score(lead_data: dict) -> int:
    score = 0
    
    employees = lead_data.get("employees", 0) or 0
    if employees >= 500:
        score += 30
    elif employees >= 100:
        score += 20
    elif employees >= 50:
        score += 10
    
    industry = (lead_data.get("industry") or "").lower()
    if industry in ["saas", "technology", "tech", "finance", "fintech"]:
        score += 25
    
    message = (lead_data.get("message") or "").lower()
    intent_keywords = ["enterprise", "solution", "pricing", "demo", "buy", "purchase", "interest"]
    if any(keyword in message for keyword in intent_keywords):
        score += 30
    
    if lead_data.get("company"):
        score += 15
    
    return min(score, 100)


def classify_lead(score: int) -> str:
    if score >= 80:
        return "Hot"
    elif score >= 50:
        return "Warm"
    else:
        return "Cold"
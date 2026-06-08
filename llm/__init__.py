from .lead_scoring import score_lead, classify_lead
from .copilot import generate_sql_query, summarize_response, generate_follow_up_email
from .email_generator import generate_automation_email

__all__ = [
    "score_lead", "classify_lead", "generate_sql_query",
    "summarize_response", "generate_follow_up_email",
    "generate_automation_email"
]
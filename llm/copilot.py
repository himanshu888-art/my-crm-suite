from openai import OpenAIError
from .client import client, settings

SQL_GENERATION_PROMPT = """
You are a SQL expert. Convert the natural language query to SQL.

Database Schema:
- leads(lead_id, name, company, email, industry, status, lead_score, category, last_contact_date, created_at)
- activities(activity_id, lead_id, activity_type, notes, created_at)
- tasks(task_id, lead_id, task_type, due_date, status)

User Query: "{query}"

Return ONLY the SQL query, nothing else. Use PostgreSQL syntax.
"""

SUMMARIZATION_PROMPT = """
Summarize these CRM query results in natural language for a sales rep.

User Query: "{query}"
Results: {results}

Return a 2-3 sentence summary in professional tone.
"""


def generate_sql_query(user_query: str) -> tuple:
    prompt = SQL_GENERATION_PROMPT.format(query=user_query)
    
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a SQL expert. Return only SQL."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    sql_query = response.choices[0].message.content.strip()
    
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:].strip()
    if sql_query.startswith("```"):
        sql_query = sql_query[3:].strip()
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3].strip()
    
    explanation = f"Generated SQL for: {user_query}"
    
    return sql_query, explanation


def summarize_response(user_query: str, results: list) -> str:
    results_str = str(results)[:500]
    
    prompt = SUMMARIZATION_PROMPT.format(query=user_query, results=results_str)
    
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You summarize CRM data professionally."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    
    return response.choices[0].message.content.strip()


def generate_follow_up_email(company: str, context: str = None, email_type: str = "follow_up") -> str:
    prompt_type = {
        "follow_up": "Write a professional follow-up email",
        "demo": "Write a demo invitation email",
        "proposal": "Write a proposal follow-up email"
    }.get(email_type, "Write a professional follow-up email")

    prompt = f"""{prompt_type} to {company}.
    Context: {context or 'General follow-up'}

    Keep it concise (150 words), friendly, and include a clear call-to-action."""
    
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a sales email writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()
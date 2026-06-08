def generate_automation_email(company: str, lead_name: str = None, context: str = "follow_up") -> str:
    templates = {
        "follow_up": f"""Subject: Following up on our conversation - {company}

Hi {lead_name or 'there'},

I hope this email finds you well. I wanted to follow up regarding {company}'s interest in our solutions.

Based on your company profile, I believe our enterprise solution could significantly benefit your operations.

Would you be available for a brief 15-minute call this week to discuss how we can help {company} achieve its goals?

Best regards,
Your Sales Team""",
        
        "demo": f"""Subject: Demo invitation for {company}

Hi {lead_name or 'there'},

Excited to show you how our platform can transform {company}'s workflow!

I'd love to schedule a personalized 30-minute demo tailored to your specific needs.

Available times this week:
- Tuesday 2PM-4PM
- Wednesday 10AM-12PM
- Thursday 3PM-5PM

Let me know what works best for you!

Best regards,
Your Sales Team""",
        
        "proposal": f"""Subject: Custom proposal for {company}

Hi {lead_name or 'there'},

Following our conversation, I've prepared a custom proposal for {company}.

Key highlights:
- Tailored solution matching your enterprise requirements
- Competitive pricing with flexible terms
- 90-day implementation roadmap
- Dedicated support team

Can we schedule a call to walk through it?

Best regards,
Your Sales Team"""
    }
    
    return templates.get(context, templates["follow_up"])
import requests

url = "http://127.0.0.1:8000/leads/"
payload = {
    "name": "Test User",
    "company": "Test Corp",
    "email": "test.user@example.com",
    "industry": "SaaS",
    "employees": 50,
    "revenue": 100000,
    "message": "Interested in AI CRM automation."
}

try:
    resp = requests.post(url, json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")

# AI CRM Suite

Integrated AI-powered CRM automation with:
- FastAPI backend for lead management, tasks, and AI copilot endpoints
- Streamlit frontend for a user-facing dashboard
- Scheduler for follow-up automation
- AI lead scoring and email generation support

## Deploy frontend to Streamlit Cloud

1. Push your repository to GitHub if you haven't already.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click "New app" and select your repository.
4. Set the main file path to `frontend/streamlit_app.py`.
5. If your backend is deployed live, set the secret `api_base_url` to the backend URL in Streamlit Cloud settings.

Example secret:

```text
api_base_url = "https://your-backend.example.com"
```

If your backend is not deployed yet, the frontend will attempt to call `http://localhost:8000`, which only works when running locally.

## Notes

- Streamlit Cloud deploys the frontend only.
- The frontend needs a live backend to function correctly.
- Use `ST_API_BASE_URL` or `secrets.api_base_url` to configure the backend endpoint.

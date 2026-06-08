# AI CRM Suite

Integrated AI-powered CRM automation with:
- FastAPI backend for lead management, tasks, and AI copilot endpoints
- Streamlit frontend for a user-facing dashboard
- Scheduler for follow-up automation
- AI lead scoring and email generation support

## Run locally

1. Activate the virtual environment:
   - PowerShell: `.\.venv\Scripts\Activate.ps1`
   - Command Prompt: `.\.venv\Scripts\activate.bat`

2. Install dependencies if needed:
   ```powershell
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Start the FastAPI backend:
   ```powershell
   .venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. Start the Streamlit frontend:
   ```powershell
   .venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py
   ```

## Deploy to GitHub

This repository can be published to GitHub using a personal access token.

1. Set a `GITHUB_TOKEN` environment variable in the same terminal session.
   - PowerShell:
     ```powershell
     $env:GITHUB_TOKEN = "YOUR_TOKEN_HERE"
     ```

2. Run the deploy helper script:
   ```powershell
   .venv\Scripts\python.exe deploy_to_github.py my-repo-name "AI CRM Automation Suite"
   ```

3. After the script finishes, open:
   ```text
   https://github.com/YOUR_USERNAME/my-repo-name
   ```

> Note: This script uploads your local project files to GitHub. It does not automatically host the application as a live service.

## Live hosting

To make the app live, deploy the backend and frontend to a hosting provider.

### Option 1: Streamlit Cloud
- Use the GitHub repository to create a new Streamlit app.
- Set `frontend/streamlit_app.py` as the entrypoint.
- Configure any required secrets on Streamlit Cloud.

### Option 2: Render / Fly / Railway
- Deploy the FastAPI backend from `backend.main:app`.
- Use `requirements.txt` as the dependency manifest.
- Add environment variables for OpenAI and database settings as needed.

## GitHub Actions

A simple CI workflow is included at `.github/workflows/ci.yml` to run tests on pushes and pull requests.

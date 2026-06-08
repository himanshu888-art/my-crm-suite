from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database.config import get_settings
from .database.session import engine, Base
from .api import leads, copilot, tasks
from .scheduler.follow_up_scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="AI CRM Automation Suite",
    description="Integrated CRM automation with AI lead scoring, copilot, and follow-up automation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(copilot.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    return {
        "app": "AI CRM Automation Suite",
        "status": "running",
        "modules": [
            "AI Lead Qualification & Scoring",
            "CRM Copilot",
            "Follow-Up Automation Engine"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
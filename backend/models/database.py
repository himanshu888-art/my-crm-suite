from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database.session import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, enum.Enum):
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    industry = Column(String(100))
    employees = Column(Integer)
    revenue = Column(Integer)
    message = Column(Text)
    status = Column(String(50), default=LeadStatus.NEW.value)
    lead_score = Column(Integer, default=0)
    category = Column(String(20))
    last_contact_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="lead", cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="activities")


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    task_type = Column(String(50), nullable=False)
    description = Column(Text)
    due_date = Column(Date)
    status = Column(String(20), default=TaskStatus.PENDING.value)
    email_draft = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="tasks")
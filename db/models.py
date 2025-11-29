from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Text
from sqlalchemy.sql import func
from ai_job_dashboard.db.db import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    job_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    salary_raw = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    currency = Column(String)
    experience = Column(String)
    job_type = Column(String)
    posted_date = Column(DateTime)
    description = Column(Text)
    skills = Column(JSON)  # list of skill strings
    raw_data = Column(JSON)  # raw payload
    created_at = Column(DateTime, server_default=func.now())

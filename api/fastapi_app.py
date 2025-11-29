from fastapi import FastAPI, HTTPException
from ai_job_dashboard.db.db import get_session
from ai_job_dashboard.db.models import Job
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware
from ai_job_dashboard.api.match_api import router as match_router


app = FastAPI(title="AI Job Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(match_router, prefix="/match")

@app.get("/jobs")
def list_jobs(limit: int = 100):
    session = get_session()
    stmt = select(Job).limit(limit)
    res = session.execute(stmt).scalars().all()
    return [{"id": j.id, "title": j.title, "company": j.company, "location": j.location, "skills": j.skills} for j in res]

@app.get("/skills/top")
def top_skills(limit: int = 20):
    session = get_session()
    # naive aggregation in Python
    stmt = select(Job).limit(1000)
    rows = session.execute(stmt).scalars().all()
    counts = {}
    for j in rows:
        for s in j.skills or []:
            counts[s] = counts.get(s,0) + 1
    top = sorted(counts.items(), key=lambda x: -x[1])[:limit]
    return [{"skill": k, "count": v} for k,v in top]

from fastapi import APIRouter, UploadFile, File
from src.nlp.embeddings import get_model
from src.db.db import get_session
from src.db.models import Job
from sqlalchemy import select
import pandas as pd
import io
import pdfplumber
import docx
import numpy as np
from src.utils.logger import get_logger
from src.ml.faiss_index import search as faiss_search
import redis
import os
import joblib

router = APIRouter()
logger = get_logger("MatchAPI")

# Redis client for caching embeddings
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL)

def extract_text_from_file(file: UploadFile):
    content = file.file.read()
    name = file.filename.lower()
    if name.endswith(".pdf"):
        text = ""
        with io.BytesIO(content) as bio:
            with pdfplumber.open(bio) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        return text
    if name.endswith(".docx") or name.endswith(".doc"):
        doc = docx.Document(io.BytesIO(content))
        txt = []
        for p in doc.paragraphs:
            txt.append(p.text)
        return "\\n".join(txt)
    # fallback: try decode
    try:
        return content.decode("utf-8", errors="ignore")
    except Exception:
        return ""

@router.post("/match/resume")
async def match_resume(file: UploadFile = File(...), top_k: int = 10):
    text = extract_text_from_file(file)
    if not text:
        return {"error":"could not parse resume"}
    model = get_model()
    emb = model.encode([text], convert_to_numpy=True)[0].astype('float32')
    # optionally cache resume embedding in redis with short TTL
    key = f"resume_emb:{hash(text)% (10**9)}"
    r.set(key, emb.tobytes(), ex=3600)
    # use FAISS search
    results = faiss_search(text, top_k=top_k)
    # fetch job details from DB for results
    session = get_session()
    out = []
    for res in results:
        job = session.query(Job).filter(Job.job_id==res["id"]).one_or_none()
        if job:
            out.append({"job_id": job.job_id, "title": job.title, "company": job.company, "score": res["score"]})
    return {"results": out}

@router.get("/job/{job_id}/similar")
def similar_jobs(job_id: str, top_k: int = 10):
    # find similar via FAISS by locating job text in meta
    session = get_session()
    job = session.query(Job).filter(Job.job_id==job_id).one_or_none()
    if not job:
        return {"error":"job not found"}
    text = (job.title or "") + " " + (job.description or "")
    results = faiss_search(text, top_k=top_k)
    out = []
    for res in results:
        if res["id"] == job_id:
            continue
        j = session.query(Job).filter(Job.job_id==res["id"]).one_or_none()
        if j:
            out.append({"job_id": j.job_id, "title": j.title, "company": j.company, "score": res["score"]})
    return {"results": out}

from fastapi import APIRouter, UploadFile, File
from src.nlp.embeddings import get_model, embed_texts
from src.db.db import get_session
from src.db.models import Job
from sqlalchemy import select
import pandas as pd
import io
import pdfplumber
import docx
from rapidfuzz import process, fuzz
import numpy as np
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger("MatchAPI")

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
        return "\n".join(txt)
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
    resume_emb = model.encode([text], convert_to_numpy=True)[0]

    # load jobs from DB
    session = get_session()
    stmt = select(Job).limit(2000)  # limit for speed
    rows = session.execute(stmt).scalars().all()
    job_texts = []
    job_ids = []
    for j in rows:
        job_texts.append((j.id, (j.title or "") + " " + (j.description or "")))
        job_ids.append(j.id)
    texts = [t[1] for t in job_texts]
    if not texts:
        return {"results":[]}
    job_embs = model.encode(texts, convert_to_numpy=True)
    # compute cosine similarity
    import numpy as np
    norms = np.linalg.norm(job_embs, axis=1) * np.linalg.norm(resume_emb)
    sims = (job_embs @ resume_emb) / (norms + 1e-9)
    top_idx = np.argsort(-sims)[:top_k]
    results = []
    for i in top_idx:
        j = rows[i]
        results.append({"job_id": j.job_id, "title": j.title, "company": j.company, "score": float(sims[i])})
    return {"results": results}

@router.get("/job/{job_id}/similar")
def similar_jobs(job_id: str, top_k: int = 10):
    model = get_model()
    session = get_session()
    rows = session.execute(select(Job)).scalars().all()
    id_to_idx = {j.job_id: idx for idx, j in enumerate(rows)}
    if job_id not in id_to_idx:
        return {"error":"job not found"}
    texts = [(j.title or "") + " " + (j.description or "") for j in rows]
    embs = model.encode(texts, convert_to_numpy=True)
    idx = id_to_idx[job_id]
    query = embs[idx]
    import numpy as np
    norms = np.linalg.norm(embs, axis=1) * np.linalg.norm(query)
    sims = (embs @ query) / (norms + 1e-9)
    top_idx = np.argsort(-sims)[1:top_k+1]  # exclude itself
    out = []
    for i in top_idx:
        j = rows[i]
        out.append({"job_id": j.job_id, "title": j.title, "company": j.company, "score": float(sims[i])})
    return {"results": out}

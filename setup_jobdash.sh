#!/usr/bin/env bash
set -euo pipefail

# 1) make a dev branch
git checkout -b feat/phase1-stealth-scrapers-faiss || true

# 2) create python venv (optional — skip if using conda)
python3 -m venv .venv
source .venv/bin/activate

# 3) basic requirements
cat > requirements.txt <<'PYREQ'
fastapi==0.95.2
uvicorn[standard]==0.22.0
playwright==1.38.1
playwright-stealth==0.1.3
requests==2.31.0
beautifulsoup4==4.12.2
aiohttp==3.9.0
celery==5.3.1
redis==4.5.1
sqlalchemy==2.1.0
alembic==1.11.1
psycopg2-binary==2.9.7
faiss-cpu==1.7.4
sentence-transformers==2.2.2
streamlit==1.26.0
spaCy==3.6.0
pdfplumber==0.8.0
python-multipart==0.0.6
python-dotenv==1.1.0
rapidfuzz==2.13.7
PYREQ

pip install -r requirements.txt

# 4) install playwright browsers
python -m playwright install --with-deps

# 5) create project layout
mkdir -p ai_job_dashboard/{scraper,workers,ml,api,streamlit,db,migrations}
touch ai_job_dashboard/__init__.py

# 6) add docker-compose for Postgres and Redis, plus web & worker service
cat > docker-compose.yml <<'DC'
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: jobdash
      POSTGRES_PASSWORD: jobdash
      POSTGRES_DB: jobdash
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  web:
    build: .
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  worker:
    build: .
    command: celery -A workers.tasks worker --loglevel=info
    volumes:
      - ./:/app
    depends_on:
      - redis
      - postgres

  streamlit:
    build: .
    command: streamlit run streamlit/app.py --server.port 8501 --server.address 0.0.0.0
    volumes:
      - ./:/app
    ports:
      - "8501:8501"
    depends_on:
      - web
      - worker

volumes:
  pgdata:
DC

# 7) Dockerfile
cat > Dockerfile <<'DF'
FROM python:3.10-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app
# expose ports for uvicorn and streamlit in compose
EXPOSE 8000 8501

# default
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
DF

# 8) minimal FastAPI API to expose FAISS search + ingestion webhook
cat > ai_job_dashboard/api/main.py <<'API'
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from ml.faiss_indexer import FAISSIndexer
import os

app = FastAPI()
indexer = FAISSIndexer(index_path=os.getenv("FAISS_INDEX", "faiss.index"))

class JobIn(BaseModel):
    id: str
    title: str
    description: str
    url: str

@app.post("/ingest")
async def ingest(job: JobIn, background_tasks: BackgroundTasks):
    # quick DB write could be added here
    background_tasks.add_task(indexer.add_job_and_persist, job.dict())
    return {"status": "queued"}

@app.get("/search")
def search(q: str, top_k: int = 10):
    results = indexer.search(q, k=top_k)
    return {"query": q, "results": results}
API

# 9) FAISS indexer (simple)
cat > ai_job_dashboard/ml/faiss_indexer.py <<'FI'
import os
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict

class FAISSIndexer:
    def __init__(self, index_path="faiss.index", mapping_path="faiss_map.json"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index_path = index_path
        self.mapping_path = mapping_path
        self.dim = 384
        self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.mapping_path, "r") as f:
                self.id_map = json.load(f)
            self.next_id = max([int(k) for k in self.id_map.keys()]) + 1
        else:
            self.index = faiss.IndexFlatIP(self.dim)
            self.id_map = {}
            self.next_id = 1

    def add_job_and_persist(self, job: Dict):
        text = job.get("title", "") + " " + job.get("description", "")
        emb = self.model.encode([text], convert_to_numpy=True)
        faiss.normalize_L2(emb)
        self.index.add(emb)
        self.id_map[str(self.next_id)] = job
        self.next_id += 1
        faiss.write_index(self.index, self.index_path)
        with open(self.mapping_path, "w") as f:
            json.dump(self.id_map, f, indent=2)

    def search(self, q: str, k=10):
        emb = self.model.encode([q], convert_to_numpy=True)
        faiss.normalize_L2(emb)
        D, I = self.index.search(emb, k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            job = self.id_map.get(str(idx+1), {})
            results.append({"score": float(score), "job": job})
        return results
FI

# 10) Celery tasks including reindex trigger
cat > ai_job_dashboard/workers/tasks.py <<'CT'
from celery import Celery
import os
from ml.faiss_indexer import FAISSIndexer
from scraper.playwright_scraper import run_scrape_for_seed

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery('tasks', broker=CELERY_BROKER_URL)

indexer = FAISSIndexer()

@app.task
def scrape_and_index(seed_url):
    # runs scraper to fetch jobs from seed and index them
    jobs = run_scrape_for_seed(seed_url)
    for job in jobs:
        indexer.add_job_and_persist(job)
    return {"ingested": len(jobs)}

@app.task
def reindex_all():
    # placeholder simple retrain / rebuild pattern
    # in prod you'd read all jobs from DB; here we re-create index from mapping if available
    indexer._load_or_create()
    return {"status": "reindexed"}
CT

# 11) Simple Playwright stealth scraper skeleton
cat > ai_job_dashboard/scraper/playwright_scraper.py <<'PS'
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
import time

async def _scrape(url, proxy=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headful fallback
        context = await browser.new_context()
        page = await context.new_page()
        # stealth available as sync wrapper; approximate by hiding navigator
        await page.add_init_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)
            html = await page.content()
            await browser.close()
            return html
        except Exception as e:
            await browser.close()
            raise

def parse_job_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    # naive pattern — customize per site
    for card in soup.select("a"):
        title = card.get_text(separator=" ", strip=True)
        href = card.get("href")
        if title and href:
            jobs.append({"id": href, "title": title, "description": "", "url": href})
    return jobs

def run_scrape_for_seed(url):
    html = asyncio.run(_scrape(url))
    return parse_job_listings(html)

if __name__ == "__main__":
    print(run_scrape_for_seed("https://remoteok.com"))
PS

# 12) Resume parser (spaCy + pdfplumber + simple NER)
cat > ai_job_dashboard/ml/resume_parser.py <<'RP'
import spacy
import pdfplumber
import re
from rapidfuzz import process, fuzz

nlp = spacy.load("en_core_web_sm")

SKILL_CANDIDATES = [
    "python","java","c++","pytorch","tensorflow","scikit-learn","docker","kubernetes",
    "aws","gcp","azure","sql","postgresql","react","nodejs"
]

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_sections(text):
    sections = {}
    # naive split by headings
    parts = re.split(r'\n[A-Z][A-Za-z ]{2,}\n', text)
    sections["full_text"] = text
    return sections

def extract_skills(text):
    found = set()
    lower = text.lower()
    for skill in SKILL_CANDIDATES:
        if skill in lower:
            found.add(skill)
    # fuzzy match additions
    tokens = re.findall(r"\b[a-zA-Z0-9\-\+\.#]+\b", text.lower())
    matches = process.extractBests(" ".join(tokens), SKILL_CANDIDATES, scorer=fuzz.partial_ratio, score_cutoff=80, limit=10)
    for m in matches:
        found.add(m[0])
    return list(found)

def parse_resume(path):
    text = extract_text_from_pdf(path)
    sections = extract_sections(text)
    skills = extract_skills(text)
    doc = nlp(text[:10000])
    ents = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ("ORG","PERSON","GPE","DATE")]
    return {"skills": skills, "sections": sections, "entities": ents}
RP

# 13) Basic Streamlit page to hit search endpoint
cat > streamlit/app.py <<'ST'
import streamlit as st
import requests

st.title("AI Job Postings Dashboard — Recommendations (demo)")
q = st.text_input("Search / Describe your ideal role", value="Senior ML Engineer, PyTorch, AWS")
if st.button("Search"):
    resp = requests.get("http://web:8000/search", params={"q": q, "top_k": 10})
    data = resp.json()
    for r in data.get("results", []):
        st.markdown(f"**{r['job'].get('title','(no title)')}** — score {r['score']:.3f}")
        st.write(r['job'].get('url'))
ST

# 14) Add basic alembic init placeholder (won't run DB migrations yet)
mkdir -p ai_job_dashboard/db
cat > ai_job_dashboard/db/__init__.py <<'DBI'
# placeholder for DB models and alembic integration
DBI

# 15) git add & commit
git add .
git commit -m "feat: bootstrap stealth playwright scraper, celery worker, faiss indexer, resume parser, streamlit UI, docker-compose"

echo "BOOTSTRAP COMPLETE. Next steps:"
echo "1) Start docker services: docker-compose up --build"
echo "2) From local machine you can call POST http://localhost:8000/ingest to add jobs (body: id,title,description,url)"
echo "3) Run Celery worker locally: celery -A ai_job_dashboard.workers.tasks worker --loglevel=info"
echo "4) Inspect Streamlit UI at http://localhost:8501"


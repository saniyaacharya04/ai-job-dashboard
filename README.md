
---
<p align="center">
  <!-- Tech Stack Badges -->
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python">
  <img src="https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi">
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit">
  <img src="https://img.shields.io/badge/FAISS-Semantic_Search-orange">
  <img src="https://img.shields.io/badge/Celery-Worker-4BC51D?logo=celery">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql">
  <img src="https://img.shields.io/badge/Redis-Queue-CC0000?logo=redis">
  <img src="https://img.shields.io/badge/Docker-Production-2496ED?logo=docker">

  <!-- CI/CD Badge -->
  <img src="https://github.com/saniyaacharya04/ai-job-dashboard/actions/workflows/ci.yml/badge.svg">

  <!-- License -->
  <img src="https://img.shields.io/badge/License-MIT-green.svg">

  <!-- Code Style -->
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg">
</p>

<p align="center">
  <!-- GitHub Stats -->
  <img src="https://img.shields.io/github/stars/saniyaacharya04/ai-job-dashboard?style=social">
  <img src="https://img.shields.io/github/forks/saniyaacharya04/ai-job-dashboard?style=social">
  <img src="https://img.shields.io/github/issues/saniyaacharya04/ai-job-dashboard">
  <img src="https://img.shields.io/github/last-commit/saniyaacharya04/ai-job-dashboard">
  <img src="https://img.shields.io/github/repo-size/saniyaacharya04/ai-job-dashboard">
</p>


# AI Job Dashboard – Intelligent Job Search Platform

Scraping • Resume Parsing • Skill Matching • Semantic Search • Streamlit • FastAPI • Celery • Redis • FAISS • Docker

A production-grade AI-powered job matching platform that:

* Crawls job boards (Indeed, LinkedIn, RemoteOK, Naukri)
* Parses resumes and extracts skills
* Computes similarity using FAISS vector search
* Detects skill gaps and missing qualifications
* Serves recommendations through FastAPI
* Visualizes insights through a Streamlit dashboard
* Runs background pipelines using Celery + Redis
* Is fully containerized with a Docker Compose service architecture

This project demonstrates real ML engineering, backend development, ETL pipelines, and scalable AI system design.

---

## Features

### 1. Web Scrapers

* Playwright with stealth mode (anti-bot)
* Proxy rotation support
* Clean job extraction to structured JSON
* Multi-site scraping support (Indeed, LinkedIn, Naukri, RemoteOK)

### 2. Semantic Job Matching (FAISS)

* SentenceTransformers (`all-MiniLM-L6-v2`)
* Cosine similarity vector search in milliseconds
* Persistent FAISS index + metadata
* Automatic index rebuilds

### 3. Resume Parsing and Skill Extraction

* spaCy Named Entity Recognition
* PDF parsing with pdfplumber
* Fuzzy skill detection using RapidFuzz
* Skill-gap analysis between resume and job requirements

### 4. Streamlit Dashboard

* Resume-to-job match scoring
* Job exploration interface
* Skill visualizations
* Similarity heatmaps and analytics

### 5. FastAPI Backend

Endpoints:

* `POST /ingest`: Add new job postings
* `GET /search`: Semantic job search
* `GET /health`: System health status

### 6. Celery Workers

* ETL pipelines
* Scheduled scraping
* Automatic FAISS index rebuilds
* Background inference jobs

### 7. Production-Ready Docker Stack

* FastAPI service
* Streamlit UI
* Redis (task queue)
* Postgres (database)
* Celery (workers)
* Nginx reverse proxy
* Playwright-ready Python base image

---

## Architecture Overview

```
             ┌────────────────┐
             │   Streamlit    │
             │  (Dashboard)   │
             └───────┬────────┘
                     │ REST
                     ▼
       ┌───────────────────────────┐
       │          FastAPI          │
       ├─────────────┬─────────────┤
       │ Resume       │ Job Search  │
       │ Parsing      │ (FAISS)     │
       └───────┬──────┴───────┬────┘
               │              │
               ▼              ▼
        ┌──────────┐    ┌───────────┐
        │ Postgres  │    │   FAISS   │
        └──────────┘    └───────────┘

               ▲               │
               │ Celery Tasks  │
               └──────┬────────┘
                      ▼
               ┌──────────┐
               │  Redis    │
               └──────────┘
```

---

## Directory Structure

```
ai_job_dashboard/
│
├── api/            # FastAPI endpoints
├── scraper/        # Web scrapers using Playwright
├── ml/             # FAISS, embeddings, resume parser
├── db/             # SQLAlchemy models, DB session
├── workers/        # Celery task pipelines
├── streamlit/      # Streamlit dashboard
├── utils/          # Logging, config, helpers
├── docker/         # Nginx configs and Docker assets
├── tests/          # Unit tests
├── models/         # Saved ML models (.gitkeep)
└── data/           # FAISS index, caches (.gitkeep)
```

---

## Docker Setup

Start the full production system:

```bash
docker-compose up --build
```

### Service URLs

| Component | URL                                            |
| --------- | ---------------------------------------------- |
| FastAPI   | [http://localhost:8000](http://localhost:8000) |
| Streamlit | [http://localhost:8501](http://localhost:8501) |
| Postgres  | port 5432                                      |
| Redis     | port 6379                                      |

---

## API Usage Examples

### Semantic Search

```bash
curl "http://localhost:8000/search?q=machine+learning"
```

### Ingest a Job Posting

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"title":"Data Scientist","description":"Python, SQL, ML","url":"https://example.com"}'
```

---

## Python Examples

### FAISS Search

```python
from ml.faiss_indexer import indexer
indexer.search("python developer")
```

### Resume Parsing

```python
from ml.resume_parser import parse_resume
parse_resume("resume.pdf")
```

---

## Installation (Without Docker)

```bash
pip install -r requirements.txt
uvicorn api.fastapi_app:app --reload
streamlit run streamlit/streamlit_app.py
```

---

## Deployment

### Recommended: Docker Compose

```bash
docker-compose up --build -d
```

### Cloud Compatible With:

* Render
* AWS ECS
* GCP Cloud Run
* Azure Container Apps
* Railway (Docker deployment)

---

## Roadmap

* LangChain-powered job Q&A
* Global salary normalization
* Enhanced LinkedIn stealth scraping
* FAISS monitoring with Prometheus
* Fully automated CI/CD deployment pipeline

---

## Contributing

Pull requests are welcome.
You can contribute new scrapers, resume parsing models, FAISS improvements, or new analytics modules.

---

## Author

**Saniya Acharya**
AI/ML Engineer • Backend Developer • Data Engineer

---



---
<p align="center">
  <img src="https://raw.githubusercontent.com/YOUR_USERNAME/ai-job-dashboard/main/assets/banner.png" width="900"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python">
  <img src="https://img.shields.io/badge/FastAPI-API-green?logo=fastapi">
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b?logo=streamlit">
  <img src="https://img.shields.io/badge/FAISS-Semantic_Search-orange">
  <img src="https://img.shields.io/badge/Celery-Workers-4BC51D?logo=celery">
  <img src="https://img.shields.io/badge/Postgres-DB-336791?logo=postgresql">
  <img src="https://img.shields.io/badge/Redis-Queue-red?logo=redis">
  <img src="https://img.shields.io/badge/Docker-Production-2496ED?logo=docker">
  <img src="https://github.com/YOUR_USERNAME/ai-job-dashboard/actions/workflows/ci.yml/badge.svg">
</p>

# 🚀 AI Job Dashboard – Intelligent Job Search Platform

Scraping • Resume Parsing • Skill Matching • Semantic Search • Streamlit • FastAPI • Celery • Redis • FAISS • Docker

A production-grade **AI-powered job matching platform** that:

- Crawls job boards (Indeed, LinkedIn, RemoteOK, Naukri)
- Parses resumes & extracts skills
- Computes similarity using **FAISS vector search**
- Detects skill gaps & missing qualifications
- Serves recommendations via **FastAPI**
- Visualizes everything in a **Streamlit dashboard**
- Runs pipelines asynchronously with **Celery + Redis**
- Fully containerized with a **Docker Compose microservice architecture**

This project showcases **real ML engineering, backend development, ETL pipelines, and scalable AI system design**.

---

# 🌟 Features

### 🔍 **1. Web Scrapers**
- Playwright + stealth mode
- Rotating proxies
- Clean job extraction → JSON → Database
- Multi-site scraping (Indeed, LinkedIn, Naukri, RemoteOK)

### 🧠 **2. Semantic Job Matching (FAISS)**
- SentenceTransformers (`all-MiniLM-L6-v2`)
- Cosine similarity search in milliseconds
- Auto indexing + fast retrieval
- Persistent database-backed metadata

### 📄 **3. Resume Parsing & Skill Extraction**
- spaCy NER
- pdfplumber parsing
- RapidFuzz for fuzzy skill detection
- Skill-gap analysis

### 📊 **4. Streamlit Dashboard**
- Resume → Job match
- Job explorer
- FAISS similarity heatmaps
- Skill visualizations

### ⚙️ **5. FastAPI Backend**
- `/search` – semantic job search  
- `/ingest` – add new job postings  
- `/health` – system health  

### 🏭 **6. Celery Workers**
- ETL pipelines  
- Scraper scheduling  
- Automatic FAISS rebuilds  
- Background inference  

### 🐳 **7. Production Docker Stack**
- FastAPI
- Streamlit
- Redis
- Postgres
- Celery worker
- Playwright-ready Python image
- Nginx reverse proxy

---

# 🏗 Architecture Overview

```

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

```

---

# 📦 Directory Structure

```

ai_job_dashboard/
│
├── api/            # FastAPI endpoints
├── scraper/        # Web scrapers (Playwright)
├── ml/             # FAISS, embeddings, resume parser
├── db/             # SQLAlchemy models
├── workers/        # Celery tasks
├── streamlit/      # Streamlit UI
├── utils/          # Logging, config, helpers
├── docker/         # Nginx configs
├── tests/          # Unit tests
├── models/         # Saved ML models (.gitkeep)
└── data/           # Local index/cache (.gitkeep)

````

---

# 🐳 Docker Setup

Start the entire system:

```bash
docker-compose up --build
````

### Services:

| Component     | URL                                            |
| ------------- | ---------------------------------------------- |
| **FastAPI**   | [http://localhost:8000](http://localhost:8000) |
| **Streamlit** | [http://localhost:8501](http://localhost:8501) |
| **Postgres**  | 5432                                           |
| **Redis**     | 6379                                           |

---

# 🧪 API Usage Examples

### 🔎 Search

```bash
curl "http://localhost:8000/search?q=machine+learning"
```

### 📥 Ingest Job

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"title":"Data Scientist","description":"Python, SQL, ML","url":"https://"}'
```

---

# 🧠 Python Examples

### FAISS Search

```python
from ml.faiss_indexer import indexer
indexer.search("python developer")
```

### Resume Parser

```python
from ml.resume_parser import parse_resume
parse_resume("resume.pdf")
```

---

# 🛠 Installation (without Docker)

```bash
pip install -r requirements.txt
uvicorn api.fastapi_app:app --reload
streamlit run streamlit/streamlit_app.py
```

---

# 🚀 Deployment

### Recommended:

```bash
docker-compose up --build -d
```

### Cloud Ready For:

* Render
* AWS ECS
* GCP Cloud Run
* Azure Container Apps
* Railway + Docker

---

# 🔮 Roadmap

* [ ] LangChain-powered job Q&A
* [ ] Global salary normalization
* [ ] LinkedIn stealth-mode improvements
* [ ] FAISS monitoring + Prometheus
* [ ] Full CI/CD auto-deployment

---

# 🤝 Contributing

PRs welcome — add new scrapers, resume parsing models, and enhanced ML modules.

---

# 🧑‍💻 Author

**Saniya Acharya**

---

# AI Job Postings Dashboard

## Quick start (local / Docker)
1. Copy `.env.example` -> `.env` and set `DATABASE_URL`.
2. Build & run with Docker-compose:
docker compose up --build

markdown
Copy code
- API: http://localhost:8000
- Streamlit: http://localhost:8501
3. Run ETL locally:
python -c "from src.etl.pipeline import run_etl; run_etl(query='data scientist', location='India')"

markdown
Copy code

## What’s included
- Scrapers: Indeed, Naukri, LinkedIn (playwright-lite)
- PostgreSQL database
- NLP: rule-based skills + embeddings
- ML: clustering + salary predictor scaffold
- API: FastAPI endpoints
- Dashboard: Streamlit
- Automation: GitHub Actions daily job

## How to extend
- Add more scrapers to `src/scraper/`
- Use spaCy NER or fuzzy matching for skills
- Add job similarity search (embeddings)
- Add resume → job matching

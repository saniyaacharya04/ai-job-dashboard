from ai_job_dashboard.scraper.indeed_scraper import IndeedScraper
from ai_job_dashboard.scraper.naukri_scraper import NaukriScraper
from ai_job_dashboard.scraper.linkedin_scraper import LinkedInScraper
from ai_job_dashboard.db.db import get_session, engine
from ai_job_dashboard.db.models import Base, Job
from ai_job_dashboard.nlp.skill_extraction import extract_skills_from_text
from ai_job_dashboard.utils.logger import get_logger
from datetime import datetime
import sqlalchemy

logger = get_logger("ETL")

def init_db():
    Base.metadata.create_all(bind=engine)

def upsert_job(session, job_dict):
    # creates or updates based on job_id
    job_id = job_dict.get("job_id")
    if not job_id:
        return
    existing = session.query(Job).filter(Job.job_id == job_id).one_or_none()
    skills = extract_skills_from_text(job_dict.get("description",""))
    if existing:
        existing.title = job_dict.get("title") or existing.title
        existing.company = job_dict.get("company") or existing.company
        existing.description = job_dict.get("description") or existing.description
        existing.location = job_dict.get("location") or existing.location
        existing.skills = skills
    else:
        new = Job(
            source=job_dict.get("source"),
            job_id=job_id,
            title=job_dict.get("title"),
            company=job_dict.get("company"),
            location=job_dict.get("location"),
            description=job_dict.get("description"),
            skills=skills,
            metadata=job_dict
        )
        session.add(new)
    session.commit()

def run_etl(query="data scientist", location="India"):
    logger.info("ETL start")
    init_db()
    session = get_session()
    # Scrapers
    ind = IndeedScraper()
    nau = NaukriScraper()
    li = LinkedInScraper(headless=True)

    results = []
    results += ind.search(query=query, location=location, max_pages=1)
    results += nau.search(query=query, location=location, max_pages=1)
    results += li.search(query=query, location=location, max_pages=1)

    for job in results:
        try:
            upsert_job(session, job)
        except Exception:
            logger.exception("Upsert failed")
    logger.info("ETL complete")

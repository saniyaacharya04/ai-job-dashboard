"""
Train salary model from DB and save pipeline.
Usage:
    python -m src.ml.train_salary_cli
"""
from ai_job_dashboard.db.db import get_session
from ai_job_dashboard.ml.salary_predictor import train_from_db
from ai_job_dashboard.utils.logger import get_logger

logger = get_logger("train_salary_cli")

def main():
    session = get_session()
    pipeline = train_from_db(session, limit=10000)
    if pipeline:
        logger.info("Training finished.")

if __name__ == '__main__':
    main()

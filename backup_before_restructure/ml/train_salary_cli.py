"""
Train salary model from DB and save pipeline.
Usage:
    python -m src.ml.train_salary_cli
"""
from src.db.db import get_session
from src.ml.salary_predictor import train_from_db
from src.utils.logger import get_logger

logger = get_logger("train_salary_cli")

def main():
    session = get_session()
    pipeline = train_from_db(session, limit=10000)
    if pipeline:
        logger.info("Training finished.")

if __name__ == '__main__':
    main()

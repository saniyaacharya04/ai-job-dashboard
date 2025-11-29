from apscheduler.schedulers.blocking import BlockingScheduler
from src.etl.pipeline import run_etl
from src.utils.logger import get_logger

logger = get_logger("Scheduler")

def job():
    logger.info("Running scheduled ETL job...")
    run_etl(query="data scientist", location="India")

def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(job, "interval", hours=12)
    logger.info("Scheduler started – ETL will run every 12 hours.")
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()

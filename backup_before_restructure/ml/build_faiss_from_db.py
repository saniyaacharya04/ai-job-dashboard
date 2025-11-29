from src.db.db import get_session
from src.db.models import Job
from src.ml.faiss_index import build_index
from src.nlp.embeddings import get_model
from src.utils.logger import get_logger

logger = get_logger("build_faiss")

def main(limit=5000):
    session = get_session()
    rows = session.query(Job).limit(limit).all()
    texts = []
    ids = []
    for j in rows:
        texts.append((j.title or "") + " " + (j.description or ""))
        ids.append(j.job_id)
    if not texts:
        logger.error("No jobs to index.")
        return
    build_index(texts, ids)

if __name__ == '__main__':
    main()

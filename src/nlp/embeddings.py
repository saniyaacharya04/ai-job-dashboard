from sentence_transformers import SentenceTransformer
from src.utils.logger import get_logger

logger = get_logger("Embeddings")
MODEL_NAME = "all-MiniLM-L6-v2"

model = None

def get_model():
    global model
    if model is None:
        logger.info(f"Loading embedding model {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
    return model

def embed_texts(texts):
    m = get_model()
    return m.encode(texts, show_progress_bar=False, convert_to_numpy=True)

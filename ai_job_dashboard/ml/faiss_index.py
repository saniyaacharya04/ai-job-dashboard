import os
import numpy as np
import faiss
import joblib
from ai_job_dashboard.nlp.embeddings import get_model
from ai_job_dashboard.utils.logger import get_logger

logger = get_logger("FaissIndex")
INDEX_PATH = "models/faiss_index.bin"
META_PATH = "models/faiss_meta.joblib"

def build_index(texts, ids, dim=None):
    model = get_model()
    emb = model.encode(texts, convert_to_numpy=True)
    dim = emb.shape[1] if dim is None else dim
    index = faiss.IndexFlatIP(dim)  # inner product over L2-normalized vectors works as cosine
    # normalize
    faiss.normalize_L2(emb)
    index.add(emb.astype('float32'))
    os.makedirs(os.path.dirname(INDEX_PATH) or ".", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    joblib.dump({"ids": ids}, META_PATH)
    logger.info(f"FAISS index saved with {len(ids)} items")
    return index

def search(query_text, top_k=10):
    model = get_model()
    qemb = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(qemb)
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("Index not found.")
    index = faiss.read_index(INDEX_PATH)
    D, I = index.search(qemb.astype('float32'), top_k)
    meta = joblib.load(META_PATH)
    ids = meta["ids"]
    results = []
    for idx, score in zip(I[0], D[0]):
        if idx < 0 or idx >= len(ids):
            continue
        results.append({"idx": int(idx), "id": ids[int(idx)], "score": float(score)})
    return results

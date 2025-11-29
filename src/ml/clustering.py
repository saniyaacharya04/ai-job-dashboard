from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from src.nlp.embeddings import embed_texts
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("Clustering")

def cluster_job_descriptions(descriptions, n_clusters=8):
    if not descriptions:
        return []
    embeddings = embed_texts(descriptions)
    # optional dimensionality reduction for stability
    if embeddings.shape[1] > 50:
        pca = PCA(n_components=50)
        emb = pca.fit_transform(embeddings)
    else:
        emb = embeddings
    kmeans = KMeans(n_clusters=min(n_clusters, len(descriptions)), random_state=42)
    labels = kmeans.fit_predict(emb)
    return labels, embeddings

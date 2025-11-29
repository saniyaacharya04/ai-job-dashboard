import joblib
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from src.utils.logger import get_logger

logger = get_logger("SalaryPredictor")
MODEL_PATH = "models/salary_rf_pipeline.joblib"

def build_features(jobs):
    """
    jobs: list of dict with keys: title, description, company, location, skills (list), experience, salary_min, salary_max
    We'll predict salary_mid = (min+max)/2 where available.
    """
    rows = []
    y = []
    for j in jobs:
        if j.get("salary_min") is None and j.get("salary_max") is None:
            continue
        title = j.get("title") or ""
        desc = (j.get("description") or "")[:1000]
        company = j.get("company") or ""
        location = j.get("location") or ""
        skills = " ".join(j.get("skills") or [])
        experience = j.get("experience") or ""
        minv = j.get("salary_min") or j.get("salary_max")
        maxv = j.get("salary_max") or j.get("salary_min")
        if minv is None:
            continue
        mid = (minv + (maxv if maxv else minv)) / 2.0
        rows.append({
            "title": title,
            "desc": desc,
            "company": company,
            "location": location,
            "skills": skills,
            "experience": experience
        })
        y.append(mid)
    return rows, np.array(y, dtype=float)

def train_from_db(session, limit=5000):
    from src.db.models import Job
    q = session.query(Job).limit(limit).all()
    jobs = []
    for j in q:
        jobs.append({
            "title": j.title,
            "description": j.description,
            "company": j.company,
            "location": j.location,
            "skills": j.skills or [],
            "experience": j.experience,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max
        })
    X_rows, y = build_features(jobs)
    if len(X_rows) == 0:
        logger.error("No labeled salary data found in DB to train.")
        return None
    # prepare pipeline
    # Text features: title + desc + skills
    text_features = ColumnTransformer([
        ("text", TfidfVectorizer(max_features=3000, ngram_range=(1,2)), "text_blob"),
    ], remainder="drop")
    # Create X matrix as dicts -> transform below
    texts = [ (r["title"] + " " + r["desc"] + " " + r["skills"]) for r in X_rows ]
    X_text = texts
    # train model
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_text, y) if hasattr(model, "fit") and isinstance(X_text, (list,)) else None
    # Note: we will wrap model + vectorizer
    from sklearn.pipeline import make_pipeline
    vect = TfidfVectorizer(max_features=3000, ngram_range=(1,2))
    pipeline = make_pipeline(vect, RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1))
    pipeline.fit(texts, y)
    os.makedirs(os.path.dirname(MODEL_PATH) or ".", exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info(f"Saved salary model to {MODEL_PATH}")
    return pipeline

def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        logger.info("No trained salary model found.")
        return None

def predict_salary(texts):
    model = load_model()
    if not model:
        raise RuntimeError("No salary model available. Train first.")
    return model.predict(texts)

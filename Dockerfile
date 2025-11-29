# -----------------------------------------
# BASE IMAGE (shared across API/worker/streamlit)
# -----------------------------------------
FROM python:3.10-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libcups2 libasound2 fonts-liberation \
    libpangocairo-1.0-0 libxss1 libxtst6 wget build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m playwright install --with-deps

RUN useradd -m jobdash
USER jobdash


# ==============================
# API IMAGE
# ==============================
FROM base AS api

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "ai_job_dashboard.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]


# ==============================
# STREAMLIT IMAGE
# ==============================
FROM base AS streamlit

EXPOSE 8501

HEALTHCHECK --interval=20s --timeout=3s CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "ai_job_dashboard/streamlit/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]


# ==============================
# WORKER IMAGE
# ==============================
FROM base AS worker

CMD ["celery", "-A", "ai_job_dashboard.workers.pipeline", "worker", "--loglevel=info"]

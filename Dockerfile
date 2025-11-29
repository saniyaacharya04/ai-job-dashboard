FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright dependencies + install browsers
RUN apt-get update && apt-get install -y wget gnupg2 libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libgtk-3-0 libdbus-1-3 libxcomposite1 libxrandr2 libasound2 libgbm1 libpangocairo-1.0-0 && \
    python -m playwright install --with-deps

COPY src/ ./src
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]

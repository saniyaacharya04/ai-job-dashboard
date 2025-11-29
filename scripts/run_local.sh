#!/usr/bin/env bash
# Run FastAPI and Streamlit locally (expects virtualenv or system Python with deps installed)
uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000 & 
streamlit run src/app/streamlit_app.py

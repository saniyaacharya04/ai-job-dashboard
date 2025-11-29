run-api:
\tuvicorn api.fastapi_app:app --reload

run-streamlit:
\tstreamlit run streamlit/streamlit_app.py

worker:
\tcelery -A workers.pipeline worker --loglevel=info

build:
\tdocker-compose build

up:
\tdocker-compose up

down:
\tdocker-compose down -v

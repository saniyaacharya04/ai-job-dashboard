import streamlit as st
import pandas as pd
from src.db.db import get_session
from src.db.models import Job
from src.utils.logger import get_logger
from sqlalchemy import select, func
import plotly.express as px
logger = get_logger("StreamlitApp")

st.set_page_config(layout="wide", page_title="AI Job Postings Dashboard")

def load_jobs(limit=1000):
    session = get_session()
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
    rows = session.execute(stmt).scalars().all()
    df = pd.DataFrame([{
        "id": j.id,
        "title": j.title,
        "company": j.company,
        "location": j.location,
        "skills": ", ".join(j.skills or []),
        "posted": j.posted_date,
        "source": j.source
    } for j in rows])
    return df

def main():
    st.title("AI Job Postings Dashboard")
    st.sidebar.header("Filters")
    q = st.sidebar.text_input("Query", "data scientist")
    loc = st.sidebar.text_input("Location", "India")
    refresh = st.sidebar.button("Run ETL (scrape once)")

    if refresh:
        with st.spinner("Running ETL..."):
            from src.etl.pipeline import run_etl
            run_etl(query=q, location=loc)
            st.success("ETL completed. Reload to see results.")

    df = load_jobs(limit=500)
    st.header("Latest jobs")
    st.dataframe(df)

    st.header("Top skills")
    # explode skills column
    if not df.empty:
        s = df["skills"].str.split(", ").explode().value_counts().head(30)
        fig = px.bar(x=s.index, y=s.values, labels={"x":"skill", "y":"count"})
        st.plotly_chart(fig, use_container_width=True)
    
    # Resume upload + matching UI
st.header("Resume → Job matching")
uploaded = st.file_uploader("Upload resume (pdf/docx)", type=["pdf","docx","doc"])
if uploaded:
    with st.spinner("Matching resume..."):
        files = {"file": (uploaded.name, uploaded.getvalue())}
        import requests, json, io
        from urllib.parse import urljoin
        try:
            # call local API
            resp = requests.post("http://127.0.0.1:8000/match/resume", files={"file": (uploaded.name, uploaded.getvalue())})
            data = resp.json()
            st.write(data)
        except Exception as e:
            st.error("Make sure FastAPI is running locally on port 8000")


if __name__ == "__main__":
    main()

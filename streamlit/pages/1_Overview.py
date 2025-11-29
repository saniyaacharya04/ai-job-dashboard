import streamlit as st
from ai_job_dashboard.db.db import get_session
from ai_job_dashboard.db.models import Job
import pandas as pd
import plotly.express as px

st.title("Market Overview")

session = get_session()
jobs = session.query(Job).limit(500).all()
df = pd.DataFrame([{
    "title": j.title,
    "company": j.company,
    "location": j.location,
    "skills": ", ".join(j.skills or [])
} for j in jobs])

st.header("Latest Jobs")
st.dataframe(df)

st.header("Top skills")
if not df.empty:
    s = df["skills"].str.split(", ").explode().value_counts().head(30)
    fig = px.bar(x=s.index, y=s.values, labels={"x":"skill", "y":"count"})
    st.plotly_chart(fig, use_container_width=True)

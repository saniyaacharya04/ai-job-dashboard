import streamlit as st
from ai_job_dashboard.db.db import get_session
from ai_job_dashboard.db.models import Job
import pandas as pd

st.title("Skills Explorer")

session = get_session()
jobs = session.query(Job).limit(2000).all()

skills = {}
for j in jobs:
    for s in j.skills or []:
        skills[s] = skills.get(s, 0) + 1

sk_df = pd.DataFrame(sorted(skills.items(), key=lambda x: -x[1]), columns=["skill","count"])
st.dataframe(sk_df.head(200))
st.download_button("Download CSV", sk_df.to_csv(index=False), file_name="skills.csv")

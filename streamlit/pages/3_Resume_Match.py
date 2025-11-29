import streamlit as st
import requests

st.title("Resume → Job Matching")

uploaded = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf","docx","doc"])
if uploaded:
    try:
        resp = requests.post(
            "http://127.0.0.1:8000/match/resume",
            files={"file": (uploaded.name, uploaded.getvalue())}
        )
        st.json(resp.json())
    except Exception as e:
        st.error("FastAPI must be running at http://127.0.0.1:8000")

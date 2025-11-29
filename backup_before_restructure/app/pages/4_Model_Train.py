import streamlit as st
import subprocess, sys

st.title("ML Model Training")

st.write("Train salary predictor model and build FAISS job similarity index.")

if st.button("Train Salary Model"):
    st.info("Training salary model...")
    subprocess.run([sys.executable, "-m", "src.ml.train_salary_cli"])
    st.success("Salary model training finished!")

if st.button("Build FAISS Index"):
    st.info("Building FAISS index...")
    subprocess.run([sys.executable, "src/ml/build_faiss_from_db.py"])
    st.success("FAISS index built!")

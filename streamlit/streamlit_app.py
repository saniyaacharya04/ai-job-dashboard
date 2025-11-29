import streamlit as st

st.set_page_config(page_title="AI Job Dashboard", layout="wide")
st.title("AI Job Dashboard")
st.markdown("Use the sidebar to navigate. This app has multiple pages: Overview, Skills, Resume Match, Model Train.")
st.sidebar.title("Pages")
st.sidebar.markdown("- Overview (default)\\n- Skills\\n- Resume Match\\n- Model Train")
st.write("Open the pages from the sidebar or use the page menu at top-right in Streamlit.")

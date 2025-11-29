from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
USER_AGENT = os.getenv("USER_AGENT", "ai-job-dashboard-bot/1.0")
PROXY_URL = os.getenv("PROXY_URL", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

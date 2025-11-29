import requests
from bs4 import BeautifulSoup
from src.utils.config import USER_AGENT, PROXY_URL
from src.utils.logger import get_logger
logger = get_logger("BaseScraper")

DEFAULT_HEADERS = {"User-Agent": USER_AGENT}

class BaseScraper:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        if PROXY_URL:
            self.session.proxies.update({"http": PROXY_URL, "https": PROXY_URL})

    def get(self, url, **kwargs):
        logger.info(f"GET {url}")
        resp = self.session.get(url, timeout=30, **kwargs)
        resp.raise_for_status()
        return resp.text

    def parse(self, html):
        return BeautifulSoup(html, "lxml")

from playwright.sync_api import sync_playwright
from src.utils.logger import get_logger
from bs4 import BeautifulSoup
import time

logger = get_logger("IndeedScraper")

class IndeedScraper:
    BASE_URL = "https://www.indeed.com/jobs?q={query}&l={location}&start={start}"

    def __init__(self, headless=True):
        self.headless = headless

    def search(self, query="data scientist", location="India", max_pages=1):
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()

            for page_no in range(max_pages):
                url = self.BASE_URL.format(
                    query=query.replace(" ", "+"),
                    location=location.replace(" ", "+"),
                    start=page_no * 10
                )

                logger.info(f"[Indeed] Navigating: {url}")
                page.goto(url, timeout=60000)

                # wait for job cards to load
                page.wait_for_selector("a.tapItem", timeout=15000)

                # scroll for lazy-loaded content
                self._auto_scroll(page)

                html = page.content()
                soup = BeautifulSoup(html, "lxml")

                cards = soup.select("a.tapItem")

                for card in cards:
                    try:
                        job = self._parse_card(card, page)
                        if job:
                            results.append(job)
                    except Exception:
                        logger.exception("Failed to parse job card")

            browser.close()
        return results

    def _auto_scroll(self, page):
        """Scrolls down to load more jobs"""
        for _ in range(5):
            page.mouse.wheel(0, 2000)
            time.sleep(0.8)

    def _parse_card(self, card, page):
        title = card.select_one("h2 span")
        title = title.get_text(strip=True) if title else ""

        company = card.select_one(".companyName")
        company = company.get_text(strip=True) if company else ""

        location = card.select_one(".companyLocation")
        location = location.get_text(strip=True) if location else ""

        job_id = card.get("data-jk")
        href = card.get("href")
        link = "https://www.indeed.com" + href if href else None

        description = ""
        if link:
            try:
                description = self._fetch_job_description(page, link)
            except Exception:
                description = ""

        return {
            "source": "indeed",
            "job_id": f"indeed-{job_id}",
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": link
        }

    def _fetch_job_description(self, page, link):
        """Open job detail in a new tab"""
        detail_page = page.context.new_page()
        detail_page.goto(link, timeout=60000)
        detail_page.wait_for_timeout(1500)

        html = detail_page.content()
        detail_soup = BeautifulSoup(html, "lxml")

        desc = detail_soup.select_one("#jobDescriptionText")

        detail_page.close()

        return desc.get_text("\n", strip=True) if desc else ""

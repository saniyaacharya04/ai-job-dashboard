from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
import time
import random
from src.utils.logger import get_logger

logger = get_logger("IndeedStealth")

class IndeedScraper:
    BASE_URL = "https://www.indeed.com/jobs?q={query}&l={location}&start={start}"

    def __init__(self, headless=False):  # headful increases success rate
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
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()

            # stealth mode
            stealth_sync(page)

            for page_no in range(max_pages):
                url = self.BASE_URL.format(
                    query=query.replace(" ", "+"),
                    location=location.replace(" ", "+"),
                    start=page_no * 10
                )

                logger.info(f"Visiting Indeed: {url}")
                page.goto(url, timeout=60000, wait_until="networkidle")

                # random mouse moves to simulate real user
                self._human_interaction(page)

                # scroll down to trigger lazy loading
                self._auto_scroll(page)

                # get page content
                html = page.content()
                soup = BeautifulSoup(html, "lxml")

                cards = soup.select("a.tapItem")
                if not cards:
                    logger.error("❌ No job cards found — likely still blocked")
                    continue

                for card in cards:
                    try:
                        data = self._parse_card(card, page)
                        if data:
                            results.append(data)
                    except Exception:
                        logger.exception("Card parse failed")

            browser.close()
        return results

    def _human_interaction(self, page):
        for _ in range(random.randint(5, 12)):
            x = random.randint(100, 1200)
            y = random.randint(100, 800)
            page.mouse.move(x, y, steps=random.randint(5, 15))
            time.sleep(random.uniform(0.05, 0.2))

    def _auto_scroll(self, page):
        for _ in range(8):
            page.mouse.wheel(0, 2000)
            time.sleep(random.uniform(0.4, 0.9))

    def _parse_card(self, card, page):
        title = card.select_one("h2 span")
        company = card.select_one(".companyName")
        location = card.select_one(".companyLocation")

        href = card.get("href")
        job_id = card.get("data-jk")

        link = "https://www.indeed.com" + href if href else None

        description = ""
        if link:
            description = self._fetch_description(page, link)

        return {
            "source": "indeed",
            "job_id": f"indeed-{job_id}",
            "title": title.get_text(strip=True) if title else "",
            "company": company.get_text(strip=True) if company else "",
            "location": location.get_text(strip=True) if location else "",
            "description": description,
            "url": link
        }

    def _fetch_description(self, page, link):
        new = page.context.new_page()
        stealth_sync(new)
        new.goto(link, timeout=60000, wait_until="networkidle")
        time.sleep(2)

        html = new.content()
        soup = BeautifulSoup(html, "lxml")
        new.close()

        desc = soup.select_one("#jobDescriptionText")
        return desc.get_text("\n", strip=True) if desc else ""

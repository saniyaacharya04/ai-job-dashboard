from src.scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
import re
from src.utils.logger import get_logger
logger = get_logger("IndeedScraper")

class IndeedScraper(BaseScraper):
    SEARCH_URL = "https://www.indeed.com/jobs?q={query}&l={location}&start={start}"

    def search(self, query="data+scientist", location="India", max_pages=2):
        jobs = []
        for page in range(max_pages):
            url = self.SEARCH_URL.format(query=query, location=location, start=page*10)
            html = self.get(url)
            soup = BeautifulSoup(html, "lxml")
            cards = soup.select("a.tapItem")
            if not cards:
                cards = soup.select(".result")
            for card in cards:
                try:
                    job = self.parse_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.exception("card parse failed")
        return jobs

    def parse_card(self, card):
        title_tag = card.select_one("h2 span") or card.select_one("h2")
        title = title_tag.get_text(strip=True) if title_tag else None
        company = card.select_one(".companyName")
        company = company.get_text(strip=True) if company else None
        location = card.select_one(".companyLocation")
        location = location.get_text(strip=True) if location else None
        job_id = card.get("data-jk") or card.get("id")
        link = "https://www.indeed.com" + card.get("href","")
        # fetch detail page for description
        try:
            detail_html = self.get(link)
            soup = BeautifulSoup(detail_html, "lxml")
            desc = soup.select_one("#jobDescriptionText")
            desc_text = desc.get_text(separator="\\n", strip=True) if desc else ""
        except Exception:
            desc_text = ""
        return {
            "source": "indeed",
            "job_id": f"indeed-{job_id}",
            "title": title,
            "company": company,
            "location": location,
            "description": desc_text,
            "url": link
        }

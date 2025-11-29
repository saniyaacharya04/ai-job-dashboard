from src.scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from src.utils.logger import get_logger
logger = get_logger("NaukriScraper")

class NaukriScraper(BaseScraper):
    SEARCH_URL = "https://www.naukri.com/{query}-jobs-in-{location}?k={query}&l={location}"

    def search(self, query="data scientist", location="Bangalore", max_pages=1):
        q = query.replace(" ", "-")
        loc = location.replace(" ", "-")
        url = self.SEARCH_URL.format(query=q, location=loc)
        html = self.get(url)
        soup = BeautifulSoup(html, "lxml")
        results = []
        for card in soup.select("article.jobTuple"):
            title = card.select_one("a.title")
            company = card.select_one("a.subTitle")
            link = title['href'] if title else None
            desc = ""
            if link:
                try:
                    desc = self.get(link)
                except Exception:
                    desc = ""
            results.append({
                "source": "naukri",
                "job_id": card.get("data-job-id", link),
                "title": title.get_text(strip=True) if title else None,
                "company": company.get_text(strip=True) if company else None,
                "location": location,
                "description": desc,
                "url": link
            })
        return results

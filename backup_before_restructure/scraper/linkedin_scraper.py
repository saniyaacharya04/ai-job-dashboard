from playwright.sync_api import sync_playwright
from src.utils.logger import get_logger
logger = get_logger("LinkedInScraper")

class LinkedInScraper:
    BASE_SEARCH = "https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&start={start}"

    def __init__(self, headless=True):
        self.headless = headless

    def search(self, query="data scientist", location="India", max_pages=1):
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            for start in range(0, max_pages*25, 25):
                url = self.BASE_SEARCH.format(query=query.replace(" ", "%20"), location=location.replace(" ", "%20"), start=start)
                logger.info(f"Visit {url}")
                page.goto(url, timeout=60000)
                page.wait_for_timeout(3000)
                job_cards = page.query_selector_all("ul.jobs-search__results-list li")
                if not job_cards:
                    # fallback selectors
                    job_cards = page.query_selector_all(".job-card-container")
                for card in job_cards:
                    try:
                        title = card.query_selector("h3") and card.query_selector("h3").inner_text().strip()
                        company = card.query_selector(".base-search-card__subtitle") and card.query_selector(".base-search-card__subtitle").inner_text().strip()
                        link_el = card.query_selector("a")
                        link = link_el.get_attribute("href") if link_el else None
                        job = {
                            "source": "linkedin",
                            "job_id": link.split("/")[-1] if link else None,
                            "title": title,
                            "company": company,
                            "location": location,
                            "description": "",  # fetch later if desired
                            "url": link
                        }
                        results.append(job)
                    except Exception:
                        logger.exception("card parse error")
            browser.close()
        return results

from playwright.sync_api import sync_playwright, BrowserContext
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
import time, random, os
from ai_job_dashboard.utils.logger import get_logger
from ai_job_dashboard.utils.proxy_pool import ProxyPool

logger = get_logger("IndeedStealth")

# Load proxies from file (optional)
def load_proxies(path="proxies.txt"):
    if not os.path.exists(path):
        return []
    with open(path,"r") as f:
        return [l.strip() for l in f.readlines() if l.strip()]

class IndeedScraper:
    BASE_URL = "https://www.indeed.com/jobs?q={query}&l={location}&start={start}"

    def __init__(self, headless=False, use_proxies=True, profile_dir="browser_profiles"):
        self.headless = headless
        self.use_proxies = use_proxies
        self.profile_dir = profile_dir
        if use_proxies:
            proxies = load_proxies()
            self.proxy_pool = ProxyPool(proxies=proxies)
        else:
            self.proxy_pool = ProxyPool(proxies=[])

    def _new_context(self, p, proxy=None, profile_name=None, user_agent=None):
        # create or reuse persistent context directory for profile reuse & cookie persistence
        persistent = None
        if profile_name:
            os.makedirs(self.profile_dir, exist_ok=True)
            persistent = os.path.join(self.profile_dir, profile_name)
        launch_args = {"headless": self.headless}
        # open browser once, create context or persistent context
        browser = p.chromium.launch_persistent_context(persistent, **launch_args) if persistent else p.chromium.launch(**launch_args).new_context()
        # Note: when using launch_persistent_context, a real user profile is used and cookies persist
        ctx = browser if persistent else browser
        # apply stealth
        try:
            stealth_sync(ctx.pages[0] if ctx.pages else ctx.new_page())
        except Exception:
            # fallback if stealth can't attach to page object
            pass
        return ctx

    def search(self, query="data scientist", location="India", max_pages=1):
        results = []
        proxies_tried = set()
        with sync_playwright() as p:
            # pick proxy if available
            proxy = self.proxy_pool.get() if self.use_proxies else None
            logger.info(f"Using proxy: {proxy}")
            # profile name to reuse cookies/profiles (randomized)
            profile_name = f"profile_{random.randint(1,1000)}"
            ctx = self._new_context(p, proxy=proxy, profile_name=profile_name)
            # ensure page exists
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            for page_no in range(max_pages):
                url = self.BASE_URL.format(query=query.replace(" ", "+"),
                                           location=location.replace(" ", "+"),
                                           start=page_no * 10)
                try:
                    logger.info(f"Visiting Indeed: {url}")
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")
                except Exception as e:
                    logger.exception("goto failed")
                    # rotate proxy and retry once
                    if self.use_proxies:
                        proxy = self.proxy_pool.get()
                        proxies_tried.add(proxy)
                        logger.info(f"Retrying with proxy {proxy}")
                        ctx.close()
                        ctx = self._new_context(p, proxy=proxy, profile_name=profile_name)
                        page = ctx.pages[0] if ctx.pages else ctx.new_page()
                        page.goto(url, timeout=60000, wait_until="domcontentloaded")
                # human-like actions
                self._human_interaction(page)
                self._auto_scroll(page)
                html = page.content()
                soup = BeautifulSoup(html, "lxml")
                cards = soup.select("a.tapItem")
                # if no cards, try different selectors (indeed sometimes uses other classes)
                if not cards:
                    cards = soup.select("div.job_seen_beacon")
                if not cards:
                    logger.error("No cards found; possible detection. rotating proxy / waiting and retrying.")
                    time.sleep(random.uniform(2,5))
                    continue
                for card in cards:
                    try:
                        job = self._parse_card(card, page)
                        if job:
                            results.append(job)
                    except Exception:
                        logger.exception("card parse failed")
            # close context
            try:
                ctx.close()
            except Exception:
                pass
        return results

    def _human_interaction(self, page):
        # small random viewport change, mouse moves and small clicks
        try:
            for _ in range(random.randint(3,7)):
                x = random.randint(50, 1200)
                y = random.randint(50, 800)
                page.mouse.move(x, y, steps=random.randint(3,12))
                time.sleep(random.uniform(0.05,0.25))
            # random hover or small click
            if random.random() < 0.3:
                page.mouse.click(random.randint(100,1100), random.randint(100,700))
                time.sleep(random.uniform(0.1,0.3))
        except Exception:
            pass

    def _auto_scroll(self, page):
        try:
            for _ in range(random.randint(4,8)):
                page.evaluate("window.scrollBy(0, window.innerHeight);")
                time.sleep(random.uniform(0.4,1.0))
        except Exception:
            pass

    def _parse_card(self, card, page):
        title = card.select_one("h2 span") or card.select_one("h2")
        company = card.select_one(".companyName") or card.select_one(".company")
        location = card.select_one(".companyLocation")
        href = card.get("href")
        job_id = card.get("data-jk") or (href.split("/")[-1] if href else None)
        link = "https://www.indeed.com" + href if href and href.startswith("/") else href

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
        try:
            newp = page.context.new_page()
            try:
                stealth_sync(newp)
            except Exception:
                pass
            newp.goto(link, timeout=60000, wait_until="domcontentloaded")
            time.sleep(random.uniform(0.8,2.0))
            html = newp.content()
            newp.close()
            soup = BeautifulSoup(html, "lxml")
            desc = soup.select_one("#jobDescriptionText") or soup.select_one(".jobsearch-jobDescriptionText")
            return desc.get_text("\n", strip=True) if desc else ""
        except Exception:
            return ""

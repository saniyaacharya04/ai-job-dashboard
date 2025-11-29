import random
import time
from src.utils.logger import get_logger
logger = get_logger("ProxyPool")

class ProxyPool:
    def __init__(self, proxies=None, health_check_url="https://www.google.com", timeout=5):
        # proxies: list of proxy strings "http://user:pass@ip:port" or "http://ip:port"
        self.proxies = proxies or []
        self.health_check_url = health_check_url
        self.timeout = timeout
        self._i = 0

    def add(self, proxy):
        self.proxies.append(proxy)

    def get(self):
        if not self.proxies:
            return None
        # round-robin
        proxy = self.proxies[self._i % len(self.proxies)]
        self._i += 1
        return proxy

    def sample(self):
        return random.choice(self.proxies) if self.proxies else None

    def health_check(self, session):
        good = []
        for p in self.proxies:
            try:
                resp = session.get(self.health_check_url, timeout=self.timeout, proxies={"http":p, "https":p})
                if resp.status_code == 200:
                    good.append(p)
            except Exception:
                logger.info(f"proxy {p} failed health check")
        self.proxies = good
        return good

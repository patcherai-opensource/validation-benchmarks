import logging
import time
import re

logger = logging.getLogger(__name__)


def _normalize_url(url, base_url):
    """Normalize URL to use the internal base URL for same-origin requests."""
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)
    # Rewrite to internal address for any localhost/loopback references
    if parsed.hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
        return urlunparse((
            base_parsed.scheme,
            base_parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        ))
    return url


def visit_url(url, base_url, admin_token):
    """Simulate an admin user visiting a URL using a headless browser."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1024,768")
    options.binary_location = "/usr/bin/chromium"

    normalized_url = _normalize_url(url, base_url)

    driver = None
    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(15)

        # Visit the app first to establish the domain for cookies
        driver.get(base_url + "/health")
        time.sleep(0.5)

        # Set admin token cookie on the application domain
        driver.add_cookie({
            "name": "session_token",
            "value": admin_token,
            "path": "/",
        })

        # Visit the reported URL
        logger.info("Admin reviewing: %s", normalized_url)
        driver.get(normalized_url)
        time.sleep(5)

        logger.info("Admin review complete: %s", normalized_url)

    except Exception as e:
        logger.error("Error reviewing %s: %s", normalized_url, str(e))
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

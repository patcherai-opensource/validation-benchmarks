"""
Headless browser XSS checker using Selenium + Chromium.
Renders HTML content and captures any JavaScript alert() calls.

Uses a JavaScript hook to intercept alert() before page content runs.
"""

import os
import time
import tempfile
import logging

logger = logging.getLogger(__name__)

# JavaScript to inject that overrides alert() and stores the message
_ALERT_HOOK = """<script>
window.__xss_alerts = [];
window.alert = function(msg) { window.__xss_alerts.push(String(msg)); };
window.confirm = function(msg) { window.__xss_alerts.push(String(msg)); return false; };
window.prompt = function(msg) { window.__xss_alerts.push(String(msg)); return null; };
</script>"""


def check_rendered_page(html_content):
    """Render HTML in a headless browser and capture alert dialog text.

    Injects an alert hook at the beginning of the HTML to capture any
    alert/confirm/prompt calls made by the page's JavaScript.

    Returns the first alert message string if triggered, or None.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    # Inject alert hook at the start of the HTML
    # Insert right after <head> or at the very beginning
    if '<head>' in html_content.lower():
        idx = html_content.lower().index('<head>') + len('<head>')
        hooked_html = html_content[:idx] + _ALERT_HOOK + html_content[idx:]
    elif '<html>' in html_content.lower():
        idx = html_content.lower().index('<html>') + len('<html>')
        hooked_html = html_content[:idx] + '<head>' + _ALERT_HOOK + '</head>' + html_content[idx:]
    else:
        hooked_html = _ALERT_HOOK + html_content

    fd, path = tempfile.mkstemp(suffix='.html', dir='/tmp')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(hooked_html)

        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')

        chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
        chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
        chrome_options.binary_location = chrome_bin

        service = Service(chromedriver_path)
        driver = None
        alert_text = None

        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(10)
            driver.get('file://' + path)

            # Wait for JS to execute
            time.sleep(2)

            # Check for captured alerts
            alerts = driver.execute_script('return window.__xss_alerts || [];')
            if alerts and len(alerts) > 0:
                alert_text = alerts[0]
        except Exception as e:
            logger.warning("Browser error: %s", str(e))
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

        return alert_text

    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

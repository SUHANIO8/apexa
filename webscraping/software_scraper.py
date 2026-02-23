import re
import logging
import pandas as pd
from datetime import datetime
from lxml import etree

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class PaloSoftwareScraper:

    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless=new")

        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--window-size=1920,1080")

        try:
            logging.info("Initializing ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
        except Exception as e:
            logging.error(f"Driver download failed: {e}")
            service = Service()

        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.wait = WebDriverWait(self.driver, 15)

    def clean_date(self, date_str):
        if not date_str or any(x in date_str.upper() for x in ["TBD", "N/A", "SUPPORT"]):
            return "N/A"

        clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str).strip()

        formats = ["%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d"]

        for fmt in formats:
            try:
                return datetime.strptime(clean, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

        return clean

    def run(self):
        try:
            url = "https://www.paloaltonetworks.com/services/support/end-of-life-announcements/end-of-life-summary"
            xpath = "//table//tbody/tr[count(td)>=3]"

            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

            tree = etree.HTML(self.driver.page_source)
            rows = tree.xpath(xpath)

            results = []

            for row in rows:
                product = " ".join(row.xpath("./td[1]//text()")).strip()
                eol = " ".join(row.xpath("./td[3]//text()")).strip()
                replacement = " ".join(row.xpath("./td[6]//text()")).strip()

                results.append({
                    "vendor": "Palo Alto",
                    "product": product,
                    "eol_date": self.clean_date(eol),
                    "replacement": replacement
                })

            df = pd.DataFrame(results)
            df.to_csv("palo_alto_sw.csv", index=False)

            logging.info(f"Saved {len(df)} software records.")

        except Exception as e:
            logging.error(f"Software scraper failed: {e}")

        finally:
            self.driver.quit()
            logging.info("Browser closed.")


if __name__ == "__main__":
    PaloSoftwareScraper().run()
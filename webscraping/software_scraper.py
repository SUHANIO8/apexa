from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = "https://www.paloaltonetworks.com/services/support/end-of-life-announcements/end-of-life-summary"

def convert_date(date_text):
    """Convert date from various formats to 'YYYY-MM-DD' format."""
    # Handle empty or whitespace-only strings
    if not date_text or not date_text.strip():
        return ""
    
    date_text = date_text.strip()
    
    # Remove ordinal suffixes (st, nd, rd, th) from day numbers
    import re
    date_text = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_text)
    
    
    formats = [
        "%B %d, %Y",    
        "%b %d, %Y",    
        "%B %d %Y",     
        "%b %d %Y",     
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: '{date_text}'")
    return ""


def setup_driver():
    """Set up Chrome WebDriver with options."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)  # Implicit wait for elements
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise


def scrape_software_eol():
    """Scrape software EOL data from Palo Alto Networks website."""
    driver = None
    data = []
    
    try:
        logger.info("Setting up WebDriver...")
        driver = setup_driver()
        
        logger.info(f"Navigating to {URL}...")
        driver.get(URL)
        
        
        logger.info("Waiting for table to load...")
        wait = WebDriverWait(driver, 20)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        # Get rows with explicit wait
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tr")))[1:]  
        
        logger.info(f"Found {len(rows)} rows in the table")
        
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            
            if len(cols) >= 4:
                product = cols[0].text
                eol = convert_date(cols[1].text)
                resource = cols[2].text
                replacement = cols[3].text

                data.append({
                    "vendor": "Palo Alto",
                    "productName": product,
                    "EOL Date": eol,
                    "resource": resource,
                    "Recommended replacement": replacement
                })
        
        logger.info(f"Successfully scraped {len(data)} records")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise
        
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver closed")
    
    return data


def save_to_csv(data, filename="software_eol.csv"):
    """Save scraped data to CSV file."""
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        print(f"software EOL data saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save data to CSV: {e}")
        raise


if __name__ == "__main__":
    try:
        logger.info("Starting software EOL Scraper...")
        data = scrape_software_eol()
        
        if data:
            save_to_csv(data)
            print(f"Successfully scraped {len(data)} software EOL records!")
        else:
            print("No data was scraped. Please check the website structure.")
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"Error: {e}")

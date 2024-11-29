import time
import logging
from selenium.webdriver.common.by import By

def google_search(driver, query, num_results=3):
    """
    Perform a Google search using Selenium and return a list of result links.
    """
    # Navigate to Google
    driver.get(f"https://www.google.com/search?q={query}&num={num_results}")

    # Wait for the page to load
    time.sleep(5)
    
    while "Our systems have detected unusual traffic from your computer" in driver.page_source:
        logging.warning("Detected unusual traffic warning. Waiting for 5 seconds.")
        time.sleep(5)

    # Extract links using the same logic as with BeautifulSoup
    links = []
    try:
        result_elements = driver.find_elements(By.XPATH, "//a[@href]")
        for element in result_elements:
            href = element.get_attribute("href")
            if href and "https://" in href and not "#" in href and not "google" in href:
                links.append(href)
    except Exception as e:
        print(f"Error extracting links: {e}")

    return links[:num_results]  # Limit the number of links
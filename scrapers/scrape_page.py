from bs4 import BeautifulSoup

def scrape_page(driver, url):
    """
    Scrape the content of a given URL using Selenium.
    """
    driver.get(url)
    driver.implicitly_wait(10)
    html_content = driver.page_source
    return html_content


def extract_text_from_html(html_content):
    """
    Extract and return the plain text from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(strip=True)
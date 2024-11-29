from scrapers.initialize import initialize_browser
from scrapers.scrape_page import scrape_page
from ai.get_ir_website import get_ir_website
from ai.process_ir_page import analyze_html_with_openai


def main(company_name):
    driver = initialize_browser()
    
    # Step 1: Get the Investor Relations Website URL
    ir_website = get_ir_website(driver, company_name)
    if not ir_website:
        print(f"Investor relations website not found for {company_name}.")
        return

    print(f"Found Investor Relations website: {ir_website}")

    # Step 2: Scrape the HTML Content
    html_content = scrape_page(driver, ir_website)
    driver.quit()

    # Step 3: Analyze the HTML with OpenAI
    structured_data = analyze_html_with_openai(html_content, ir_website)
    print(f"Structured Data:")
    print(structured_data)


if __name__ == "__main__":
    company_name = "Apple Inc."  # Replace with the desired company
    main(company_name)

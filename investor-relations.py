import csv
import json
import os
import logging
from typing import Dict, Optional, Any

from scrapers.initialize import initialize_browser
from scrapers.scrape_page import scrape_page, extract_text_from_html
from ai.get_ir_website import get_ir_website
from ai.process_ir_page import analyze_html_with_openai

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

def convert_to_json_serializable(obj: Any) -> Any:
    """
    Recursively convert custom objects to JSON-serializable format.
    
    Args:
        obj: Object to be converted
    
    Returns:
        JSON-serializable representation of the object
    """
    if hasattr(obj, '__dict__'):
        return {k: convert_to_json_serializable(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    else:
        return obj

def process_stock(driver, symbol: str, company_name: str) -> Optional[Dict]:
    """
    Process a single stock's investor relations information.
    
    Args:
        driver: Selenium WebDriver
        symbol: Stock symbol
        company_name: Company name
    
    Returns:
        Dict with scraping results or None if failed
    """
    try:
        logging.info(f"Processing stock: {symbol} - {company_name}")
        
        ir_website = get_ir_website(driver, company_name)
        if not ir_website:
            logging.warning(f"Investor relations website not found for {company_name} ({symbol}).")
            return None

        logging.info(f"Found Investor Relations website for {symbol}: {ir_website}")

        html_content = scrape_page(driver, ir_website)

        structured_data = analyze_html_with_openai(html_content)
        logging.info(f"Structured data extracted for {symbol}: {company_name}")
        
        processed_data = {
            "symbol": symbol,
            "company_name": company_name,
            "ir_website": ir_website,
            "structured_data": convert_to_json_serializable(structured_data)
        }

        output_json = f"./output/{symbol}.json"        
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, 'w', encoding='utf-8') as jsonfile:
            json.dump(processed_data, jsonfile, indent=2, ensure_ascii=False)
            logging.info(f"Structured data saved to {output_json}")
            
        return True

    except Exception as e:
        logging.error(f"Error processing {symbol} - {company_name}: {str(e)}", exc_info=True)
        return None

def main(input_csv: str):
    """
    Process all stocks from CSV and store results in JSON.
    
    Args:
        input_csv: Path to input CSV file
    """

    results = []

    driver = initialize_browser()
    logging.info(f"Browser initialized.")

    try:
        with open(input_csv, 'r') as csvfile:
            logging.info(f"Reading CSV file: {input_csv}")
            
            next(csvfile)
            
            csvreader = csv.reader(csvfile)

            count = 0
            for row in csvreader:
                if len(row) >= 2:
                    symbol, company_name = row[0], row[1]

                    if not symbol or not company_name:
                        logging.warning(f"Invalid row found: {row}")
                        continue

                    stock_result = process_stock(driver, symbol, company_name)

                    if stock_result:
                        count += 1
                        logging.info(f"Processed {count} stocks so far.")
                        
                    if count >= 5:
                        logging.info(f"Processing limit reached (10 stocks).")
                        break
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}", exc_info=True)
    finally:
        driver.quit()
        logging.info("Browser closed.")

    logging.info(f"Processed {len(results)} stocks in total.")

if __name__ == "__main__":
    INPUT_CSV = './data/stocks.csv'

    logging.info("Starting stock processing script.")
    main(INPUT_CSV)
    logging.info("Script execution completed.")
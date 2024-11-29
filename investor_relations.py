import csv
import json
import os
import logging
import asyncio
from typing import Dict, Optional, Any
from scrapers.initialize import initialize_browser
from scrapers.scrape_page import scrape_page
from scrapers.process_section import process_section_data
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

async def process_stock(driver, symbol: str, company_name: str, output_path: str) -> Optional[Dict]:
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

        sections_data = analyze_html_with_openai(html_content,ir_website)
        logging.info(f"Sections data extracted for {symbol}: {company_name}")
        
        print(len(sections_data))
        
        structured_data = await process_section_data(sections_data)
        logging.info(f"Structured data processed for {symbol}: {company_name}")
        
        processed_data = {
            "symbol": symbol,
            "company_name": company_name,
            "ir_website": ir_website,
            "structured_data": structured_data
        }
       
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(processed_data, jsonfile, indent=2, ensure_ascii=False)
            logging.info(f"Structured data saved to {output_path}")
            
        return True

    except Exception as e:
        logging.error(f"Error processing {symbol} - {company_name}: {str(e)}", exc_info=True)
        return None

async def main(input_csv: str):
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
                    
                    output_path = f"./output/{symbol}.json"
                    if os.path.exists(output_path):
                        logging.info(f"Stock {symbol} already processed. Skipping.")
                        continue

                    stock_result = await process_stock(driver, symbol, company_name, output_path)

                    if stock_result:
                        count += 1
                        logging.info(f"Processed {count} stocks so far.")
                        
                    # if count >= 1:
                    #     logging.info(f"Processing limit reached (10 stocks).")
                    #     break
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}", exc_info=True)
    finally:
        driver.quit()
        logging.info("Browser closed.")

    logging.info(f"Processed {len(results)} stocks in total.")

if __name__ == "__main__":
    INPUT_CSV = './data/companies_part2.4.csv'

    logging.info("Starting stock processing script.")
    asyncio.run(main(INPUT_CSV))
    logging.info("Script execution completed.")
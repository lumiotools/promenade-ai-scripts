import csv
import json
import os
import logging
import asyncio
from typing import Dict, Optional, Any
from scrapers.initialize import initialize_browser
from scrapers.list_sec_filings import list_sec_filings
from scrapers.process_section import process_sec_filings
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import Document

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

pinecone = Pinecone()
pinecone_index_name = "sec-filings"

pinecone_index = pinecone.Index(pinecone_index_name)

# Initialize VectorStore
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

embed_model = OpenAIEmbedding(model="text-embedding-3-small")

pipeline = IngestionPipeline(
    transformations=[
        SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=embed_model,
        ),
        embed_model,
    ],
    vector_store=vector_store, # Our new addition
)

def isIndexed(url):
    query_response = pinecone_index.query(
    vector=[0] * 1536,  # Zero vector of appropriate dimensionality
    # Your metadata filter
    filter={"url": {"$eq": url}},
    top_k=1,
    )
    
    if len(query_response.matches) > 0:
        return True
    else:
        return False



async def index_sec_filings(symbol: str, company_name: str) -> bool:
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
        logging.info(f"Processing sec filing: {symbol} - {company_name}")

        sec_filings = list_sec_filings(symbol)

        filings_content = await process_sec_filings(sec_filings,symbol)
        
        for filing in filings_content:
            content = f"Company: {company_name}\nsec_filing_form_type: {filing["form_type"]}\nfiled_on: {filing['filed']}\nperiod: {filing['period']}\nURL: {filing["url"]}\nContent: {filing['content']}"
            document = Document(doc_id=filing["url"], text=content)
            document.metadata.update({
                "symbol": symbol,
                "company_name": company_name,
                "ir_website": filing["sec_filing_website"],
                "form_type": filing["form_type"],
                "filed": filing["filed"],
                "period": filing["period"],
                "url": filing["url"],
            })
            
            try:
                pipeline.run(documents=[document])
                logging.info(f"Indexed {filing['form_type']} for {company_name}")
            except Exception as e:
                logging.error(f"Error indexing {filing['form_type']} for {company_name}: {e}")

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

                    sec_filing_indexing_done = await index_sec_filings(symbol, company_name)

                    if sec_filing_indexing_done:
                        count += 1
                        logging.info(f"Processed {count} stocks so far.")

                    if count >= 1:
                        logging.info(f"Processing limit reached (10 stocks).")
                        break
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}", exc_info=True)

    logging.info(f"Processed {len(results)} stocks in total.")

if __name__ == "__main__":
    INPUT_CSV = './data/companies_part2.3.csv'

    logging.info("Starting stock processing script.")
    asyncio.run(main(INPUT_CSV))
    logging.info("Script execution completed.")

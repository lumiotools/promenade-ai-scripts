import pandas as pd
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
from scrapers.process_section import process_link
from crawl4ai import AsyncWebCrawler
from parse_html_and_get_links import analyze_html_with_openai
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core import Document


pinecone = Pinecone()

pinecone_index_name = "nasdaq-companies"

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
    print("Checking url is existing")
    query_response = pinecone_index.query(
    vector=[0] * 1536,  # Zero vector of appropriate dimensionality
    # Your metadata filter
    filter={"url": {"$eq": url}},
    top_k=1,
    )
    if len(query_response["matches"]) > 0:
        return False
    else:
        return True

async def process_transcripts_links(transcripts_links,site_url,symbol):
     try:
        async with AsyncWebCrawler() as crawler:
            documents = []
            for transcript in transcripts_links:
                url=f"https://www.fool.com{transcript["url"]}"
                print(url)
                if isIndexed(url):
                        print(f"processing {url}")
                        markdown_content = await process_link(crawler,url)
                        content=f"Title: {transcript['title']}\nURL: {url}\nContent: {markdown_content}"
                        document = Document(doc_id=url, text=content)
                        document.metadata.update({
                            "symbol": symbol,
                            "earnings_call_website": site_url,
                            "title": transcript["title"],
                            "url": url
                            })
                        documents.append(document)
                        try:
                            pipeline.run(documents=documents)
                            logging.info(f"Indexed {site_url}")
                        except Exception as e:
                            logging.error(f"Error indexing {url}: {e}")
                else:
                    print("site indexed")
     except Exception as e:
            print("error scrapping")
            print(e)

          

async def process_stock(symbol):
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

        logging.info(f"symbol : {symbol}")

        # html_content = scrape_page(driver, ir_website)
        site_url=f"https://www.fool.com/quote/nasdaq/{symbol.lower()}/#quote-earnings-transcripts"
        async with AsyncWebCrawler() as crawler:
            page_content = await process_link(crawler,site_url)
            print("page_content")
            transcripts_links=analyze_html_with_openai(page_content)
            print("transcripts_links",transcripts_links)
            if len(transcripts_links) > 0:
                await process_transcripts_links(transcripts_links,site_url,symbol)
            else :
                 print("No transcripts found")
                     
                 

    except Exception as e:
        logging.error(f"Error processing symbol:{symbol} : {str(e)}", exc_info=True)



async def main(symbol: str):
            await process_stock(symbol)

if __name__ == "__main__":
    company_symbol = pd.read_csv("data/companies_part1.3.csv")["Symbol"].values
    for index, symbol in enumerate(company_symbol):
        print(symbol)
        asyncio.run(main(symbol))
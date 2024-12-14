from pinecone import Pinecone
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.vector_stores.pinecone import PineconeVectorStore
from dotenv import load_dotenv
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

load_dotenv()

pinecone = Pinecone()
pinecone_index_name = "nasdaq-companies"

pinecone_index = pinecone.Index(pinecone_index_name)

def isSecIndexed(symbol):
    nodes = pinecone_index.query(include_metadata=True,include_values=False,vector=[0] * 1536, top_k=1,filter={
        "symbol":symbol,
        "filed": {"$exists": True}
    } )
    return len(nodes.matches) > 0

def isIRIndexed(symbol):
    nodes = pinecone_index.query(include_metadata=True,include_values=False,vector=[0] * 1536, top_k=1,filter={
        "symbol":symbol,
        "section_name": {"$exists": True}
    } )
    return len(nodes.matches) > 0

def isEarningsCallIndexed(symbol):
    nodes = pinecone_index.query(include_metadata=True,include_values=False,vector=[0] * 1536, top_k=1,filter={
        "symbol":symbol,
        "earnings_call_website": {"$exists": True}
    } )
    return len(nodes.matches) > 0


async def main(input_csv: str):
    
    not_indexed = []
    
    with open('not_indexed.json', 'r') as f:
        not_indexed = json.load(f)
        
    try:
        with open(input_csv, 'r') as csvfile:
            logging.info(f"Reading CSV file: {input_csv}")

            next(csvfile)

            csvreader = csv.reader(csvfile)

            for index, row in enumerate(csvreader):
                        
                if len(row) >= 2:
                    symbol, company_name = row[0], row[1]
                    

                    if not symbol or not company_name:
                        logging.warning(f"Invalid row found: {row}")
                        continue
                    
                    if index <=1824:
                        continue

                    is_sec_indexed = isSecIndexed(symbol)
                    is_ir_indexed = isIRIndexed(symbol)
                    is_earnings_call_indexed = isEarningsCallIndexed(symbol)
                    
                    data = {}
                    
                    if not is_sec_indexed:
                        data["sec"] = False
                    
                    if not is_ir_indexed:
                        data["ir"] = False
                        
                    if not is_earnings_call_indexed:
                        data["earnings_call"] = False
                        
                    if  not is_sec_indexed or not is_ir_indexed or not is_earnings_call_indexed:
                        not_indexed.append({
                            "symbol": symbol,
                            "company_name": company_name,
                            "status": data
                        })
                        
                        with open('not_indexed.json', 'w') as f:
                            json.dump(not_indexed, f, indent=4)
                        
                    
                    logging.info(f"Processed {index} rows.")
            
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}", exc_info=True)
    

if __name__ == "__main__":
    INPUT_CSV = './data/companies.csv'

    logging.info("Starting stock processing script.")
    asyncio.run(main(INPUT_CSV))
    logging.info("Script execution completed.")
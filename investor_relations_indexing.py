from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import Document
from dotenv import load_dotenv
import json
import os
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("indexing.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

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


def index_company_data(symbol):
    with open(f"output/{symbol}.json", "r", encoding="utf8") as f:
        company_data = json.load(f)
        logging.info(f"Indexing {symbol}")

        company_symbol = company_data["symbol"]
        company_name = company_data["company_name"]
        company_ir_website = company_data["ir_website"]
        structured_data = company_data["structured_data"]
        
        documents = []

        for section in structured_data:
            section_name = section["section_name"]
            logging.info(f"Indexing {section_name} for {company_name}")

            for link in section["links"]:
                if isIndexed(link["url"]):
                    logging.info(f"Document {link['title']} already exists. Skipping ingestion.")
                    continue

                content = f"Company: {company_name}\nSection: {section_name}\nTitle: {link['title']}\nURL: {link['url']}\nContent: {link['content']}"
                document = Document(doc_id=link["url"], text=content)
                document.metadata.update({
                    "symbol": company_symbol,
                    "company_name": company_name,
                    "ir_website": company_ir_website,
                    "section_name": section_name,
                    "title": link["title"],
                    "url": link["url"],

                })
                
                documents.append(document)
                
        try:
            pipeline.run(documents=documents)
            logging.info(f"Indexed {company_name}")
        except Exception as e:
            logging.error(f"Error indexing {company_name}: {e}")


if __name__ == "__main__":
    company_symbol = pd.read_csv("data/companies_part3.4.csv")["Symbol"].values
    for index, symbol in enumerate(company_symbol):

        logging.info(f"Indexing {symbol} ({index+1}/{len(company_symbol)})")

        if os.path.exists(f"output/{symbol}.json"):
            index_company_data(symbol)
            logging.info(f"Indexed {symbol}")
        else:
            logging.warning(f"Skipping {symbol} as no data found")

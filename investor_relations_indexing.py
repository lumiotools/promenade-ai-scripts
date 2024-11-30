from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import Document
from llama_index.core.storage.docstore import SimpleDocumentStore
from dotenv import load_dotenv
from ai.get_embedding import get_embedding
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

if not os.path.exists("docstore.json"):
    with open("docstore.json", "w") as f:
        f.write("{}")

docstore = SimpleDocumentStore.from_persist_path(persist_path="docstore.json")

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
    docstore=docstore,
)


def index_company_data(symbol):
    with open(f"output/{symbol}.json", "r", encoding="utf8") as f:
        company_data = json.load(f)
        logging.info(f"Indexing {symbol}")

        company_symbol = company_data["symbol"]
        company_name = company_data["company_name"]
        company_ir_website = company_data["ir_website"]
        structured_data = company_data["structured_data"]

        for section in structured_data:
            section_name = section["section_name"]
            logging.info(f"Indexing {section_name} for {company_name}")

            for link in section["links"]:
                if docstore.document_exists(document.doc_id):
                    logging.info(f"Document {document.doc_id} already exists. Skipping ingestion.")
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

                pipeline.run(documents=[document])
                docstore.persist("docstore.json")

                logging.info(f"Indexed {link['title']} for {company_name}")


if __name__ == "__main__":
    company_symbol = pd.read_csv("data/companies_part.csv")["Symbol"].values
    for index, symbol in enumerate(company_symbol):

        logging.info(f"Indexing {symbol} ({index+1}/{len(company_symbol)})")

        if os.path.exists(f"output/{symbol}.json"):
            index_company_data(symbol)
            logging.info(f"Indexed {symbol}")
        else:
            logging.warning(f"Skipping {symbol} as no data found")

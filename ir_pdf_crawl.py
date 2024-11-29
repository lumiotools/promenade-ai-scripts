import os
import json
import asyncio
import requests
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import pdfplumber
from tenacity import retry, stop_after_attempt, wait_exponential
import investor_relations

# Helper function to make objects JSON serializable
def serialize(obj):
    if hasattr(obj, "__dict__"):
        return obj.__dict__  # Convert objects to dictionaries
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]  # Handle lists of objects
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}  # Handle nested dictionaries
    else:
        return str(obj) 
# Helper function for PDF extraction
def extract_pdf_content(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open("temp.pdf", "wb") as file:
            file.write(response.content)
        text = ""
        with pdfplumber.open("temp.pdf") as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF content: {str(e)}"

# Async function to process structured data
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
async def process_link(crawler, link):
    if link.url.endswith(".pdf"):
        return extract_pdf_content(link.url)
    else:
        result = await crawler.arun(
            url=link.url,
            extraction_strategy=LLMExtractionStrategy(
                provider="openai/gpt-4o",
                api_token=os.getenv("OPENAI_API_KEY"),
                instruction="Extract relevant content from the page related to the financial history, quarter results, transcripts financial statements.",
            ),
            bypass_cache=True,
        )
        return result.extracted_content

async def process_data(data):
    async with AsyncWebCrawler(verbose=True) as crawler:
        output = []

        for section in data:
            section_output = {
                "section_name": section.section_name,
                "metadata": section.metadata,
                "links": []
            }

            for link in section.links:
                content = await process_link(crawler, link)
                section_output["links"].append({
                    "title": link.title,
                    "url": link.url,
                    "content": content
                })

            output.append(section_output)

        return output



# Main function to run the processing
async def main():
    company_name = "Apple Inc."
    structured_data = investor_relations.main(company_name)
    processed_output = await process_data(structured_data)
     # Save the output to JSON file
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(processed_output, f, default=serialize, indent=4)

    print("Processing complete. Output saved to 'output.json'.")

asyncio.run(main())

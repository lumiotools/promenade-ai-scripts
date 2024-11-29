from pdf_extractor import extract_pdf_content
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import os


async def process_link(crawler, link):
    if link.url.endswith(".pdf"):
        return extract_pdf_content(link.url)
    else:
        result = await crawler.arun(
            url=link.url,
            extraction_strategy=LLMExtractionStrategy(
                provider="openai/gpt-4o-mini",
                api_token=os.getenv("OPENAI_API_KEY"),
                instruction="Extract relevant content from the page related to the financial history, quarter results, transcripts financial statements.",
            ),
            bypass_cache=True,
        )
        return result.extracted_content
    
async def process_section_data(sections):
    async with AsyncWebCrawler(verbose=True) as crawler:
        output = []

        for section in sections:
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
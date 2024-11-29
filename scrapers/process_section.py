from scrapers.pdf_extractor import extract_pdf_content
from crawl4ai import AsyncWebCrawler


async def process_link(crawler, link):
    if link.endswith(".pdf"):
        return extract_pdf_content(link)
    else:
        result = await crawler.arun(
            url=link,
            excluded_tags=['nav', 'footer', 'aside'],            
            bypass_cache=True,
        )
        return result.markdown


async def process_section_data(sections):

    async with AsyncWebCrawler() as crawler:
        output = []

        for section in sections:
            section_output = {
                "section_name": section["section_name"],
                "links": []
            }

            for link in section["links"]:
                try:
                    # Scrape content for each link
                    content = await process_link(crawler, link["url"])
                    section_output["links"].append({
                        "title": link["title"],
                        "url": link["url"],
                        "content": content
                    })
                except Exception as e:
                    # Handle potential errors during link processing
                    section_output["links"].append({
                        "title": link["title"],
                        "url": link["url"],
                        "content": f"Error processing link: {str(e)}"
                    })

            output.append(section_output)

        return output

from scrapers.pdf_extractor import extract_pdf_content
from crawl4ai import AsyncWebCrawler
from ai.process_ir_page import analyze_page_content_with_openai


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
                    
                    
                    internal_links = analyze_page_content_with_openai(content,link["url"])
                    
                    print(f"Found Internal links: {len(internal_links)}")
                    
                    for internal_link in internal_links:
                        # Scrape content for each link
                        internal_content = await process_link(crawler, internal_link["url"])
                        section_output["links"].append({
                            "title": internal_link["title"],
                            "url": internal_link["url"],
                            "content": internal_content
                        })
                        
                except Exception as e:
                    # Handle potential errors during link processing
                    print(f"Error processing link: {str(e)}")

            output.append(section_output)

        return output


async def process_sec_filings(filings,symbol):
    
    secFilingWebsite = f"https://www.nasdaq.com/market-activity/stocks/{symbol.lower()}/sec-filings?sortColumn=filed&sortOrder=desc"
    
    async with AsyncWebCrawler() as crawler:
        output = []

        for filing in filings:
            try:
                # Scrape content for each link
                content = await process_link(crawler, filing["view"]["htmlLink"])
                output.append({
                    "sec_filing_website": secFilingWebsite,
                    "form_type": filing["formType"],
                    "filed": filing["filed"],
                    "period": filing["period"],
                    "url": filing["view"]["htmlLink"],
                    "content": content
                })
            except Exception as e:
               print(f"Error processing filing: {str(e)}")

        return output
    
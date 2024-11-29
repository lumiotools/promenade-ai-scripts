from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from scrapers.initialize import initialize_browser
from scrapers.google_search import google_search

load_dotenv()

openai = OpenAI()

def get_ir_website(driver, companyName):
    searchQuery = f"{companyName} investor relations website"
    websiteUrls = google_search(driver, searchQuery)

    class ResponseFormat(BaseModel):
        url: str

    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=ResponseFormat,
        messages=[
            {"role": "system", "content": "You are a financial analyst looking for the investor relations website of a company. You will be given the list of websites fron that you need to find the correct investor relation website of that company."},
            {"role": "user", "content": f"Can you help me find the correct investor relations website of {companyName} forn the below urls: " + str(websiteUrls)},
        ])

    return response.choices[0].message.parsed.url
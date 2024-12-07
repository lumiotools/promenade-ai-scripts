from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel
import json
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

openai = OpenAI()


class Link(BaseModel):
    title: str
    url: str


class Earnings_Transcripts(BaseModel):
    earnings_call_transcripts: List[Link]

def analyze_html_with_openai(markdown_content):
    """
    Analyze page content using OpenAI and extract structured data.
    """
    prompt = f"""
You are a data extraction model. Your task is to extract **only the earnings call transcripts** from the provided markdown text. 

### Instructions:
- Only extract the **titles** and **URLs** of earnings call transcripts.
- Do **not modify** the content of the title or URL. They should be returned exactly as they appear in the markdown.
- If there are no earnings call transcripts found in the markdown, **do not return anything**.
- Each earnings call transcript is in the form of a markdown hyperlink: `[Title](URL)`.
- Extract the **title** (the part before the parentheses) and the **URL** (the part inside the parentheses).
  
The markdown content is as follows:
{markdown_content}
"""

    try:
        response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=Earnings_Transcripts,
        messages=[{"role": "user", "content": prompt}]
        )
        print("open ai")
        # print(json.loads(response.choices[0].message.content)["earnings_call_transcripts"])
        # if not response or 'earnings_call_transcripts' not in response:
        #         logging.warning("No earnings call transcripts found.")
        #         return []
        return json.loads(response.choices[0].message.content)["earnings_call_transcripts"]
    except Exception as e:
         print("Error")
         print(e)
         return []

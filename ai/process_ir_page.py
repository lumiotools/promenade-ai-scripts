from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel
import json


load_dotenv()

openai = OpenAI()

class Link(BaseModel):
    title: str
    url: str

class Metadata(BaseModel):
    name: str
    value: str


class Section(BaseModel):
    section_name: str
    links: List[Link]


class InvestorRelationsData(BaseModel):
    sections: List[Section]


def analyze_html_with_openai(html_content,ir_website):
    """
    Analyze page content using OpenAI and extract structured data.
    """
    prompt = f"""
    You are an expert content analyzer. Analyze the following content and extract structured data with the following schema:
    - Section Name: (e.g., "News Articles", "Financial Reports", "Press Releases") include all the sections present in the page content that are important for an investor relations page.
    - Links: List of links in that section these links should be exact links of articles or .pdf files (with titles and URLs)
    
    *Note: we will ignore the links that include the date before 2024*
    
    All the links needs to be in full URL format.
    This is the current website url: {ir_website}
    if any link is not in full URL format, please make it full URL by adding the website url before the link.

    Web page Content:
    {html_content}
    """
    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=InvestorRelationsData,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.parsed.model_dump_json())["sections"]

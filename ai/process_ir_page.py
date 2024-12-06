from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel
import json
from urllib.parse import urlparse


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
    - Section Name: (e.g., "News Articles", "Financial Reports", "Press Releases") include all such sections present in the page content that are important for an investor relations page.
    - Links: List of links in those section these links should be exact links of articles or .pdf files (with titles and URLs)
    
    *Note: we will ignore the links that include the date before 2024*
    
    All the links needs to be in full URL format.
    This is the current website url: {"https://"+urlparse(ir_website).netloc}
    if any link is not in full URL format, please append it to the base url and make it full URL.

    Web page Content:
    {html_content}
    """
    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=InvestorRelationsData,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.parsed.model_dump_json())["sections"]

class InternalLinks(BaseModel):
    links: List[Link]

def analyze_page_content_with_openai(html_content,page_url):
    """
    Analyze page content using OpenAI and extract structured data.
    """
    prompt = f"""
    You are an expert content analyzer. Analyze the following content and extract internal links with the following schema:
    - Links: List of links in page content these links should be exact links of articles or .pdf files (with titles and URLs)
    
    *Note: we will ignore the links that include the date before 2024*
    *Note: we will ignore the links that are belonged to other websites*
    
    All the links needs to be in full URL format.
    This is the current website url: {page_url}
    if any link is not in full URL format, please reform the full url using the above website url.

    Web page Content:
    {html_content}
    """
    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=InternalLinks,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.parsed.model_dump_json())["links"]

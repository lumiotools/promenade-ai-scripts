from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
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
    metadata: List[Metadata]


class InvestorRelationsData(BaseModel):
    sections: List[Section]


def analyze_html_with_openai(html_content):
    """
    Analyze HTML content using OpenAI and extract structured data.
    """
    prompt = f"""
    You are an expert web content analyzer. Analyze the following HTML and extract structured data with the following schema:
    - Section Name: (e.g., "News", "Financial Reports")
    - Links: List of links in that section these links should be exact links of articles or .pdf files (with titles and URLs)
    - Metadata: Additional metadata (e.g., date, author, description)

    HTML Content:
    {html_content}
    """
    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=InvestorRelationsData,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.parsed.sections

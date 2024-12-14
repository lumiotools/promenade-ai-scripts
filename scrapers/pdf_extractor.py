import requests
import pdfplumber

def extract_pdf_content(pdf_url):
    try:
        response = requests.get(pdf_url,headers={'User-Agent': 'Mozilla/5.0'},timeout=30)
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
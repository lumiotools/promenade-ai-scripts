import requests

def list_sec_filings(symbol: str):
    
    baseUrl = f"https://api.nasdaq.com/api/company/{symbol.upper()}/sec-filings?sortColumn=filed&sortOrder=desc"
    print(baseUrl)
    
    response = requests.get(baseUrl, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    
    body = response.json()
    
    if body["status"]["rCode"] != 200:
        raise Exception(f"Failed to fetch data for {symbol} - {body["status"]["bCodeMessage"][0]["errorMessage"]}")
    
    data = body["data"]["rows"]
    
    
    # TODO Filter Latest Filings Types
    
    return data
    
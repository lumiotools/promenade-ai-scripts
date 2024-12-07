import requests
from urllib import parse

def list_sec_filings(symbol: str):
    """
    Fetch and filter SEC filings for a given symbol, returning only the latest filing for each form type.
    
    Args:
        symbol (str): The stock symbol to fetch filings for.
        
    Returns:
        dict: Dictionary with form types as keys and their latest filing as values.
    """
    base_url = f"https://api.nasdaq.com/api/company/{symbol.upper().replace("-","%25sl%25")}/sec-filings?sortColumn=filed&sortOrder=desc"
    print(f"Fetching data from: {base_url}")
    
    response = requests.get(base_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    body = response.json()
    
    if body["status"]["rCode"] != 200:
        raise Exception(f"Failed to fetch data for {symbol} - {body['status']['developerMessage']}")
    
    data = body["data"]["rows"]
    
    # Filter Latest Filings by Form Type
    filtered_filings = {}
    for row in data:
        form_type = row.get("formType")
        if form_type and form_type not in filtered_filings:
            filtered_filings[form_type] = row
    
    filterRowList=[]
    for data in filtered_filings.values():
        filterRowList.append(data)

        
    return filterRowList

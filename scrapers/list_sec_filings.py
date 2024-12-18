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


def list_prev_3_years_sec_filings(symbol: str):
    """
    Fetch and filter SEC filings for a given symbol, returning only the latest filing for each form type.

    Args:
        symbol (str): The stock symbol to fetch filings for.

    Returns:
        dict: Dictionary with form types as keys and their latest filing as values.
    """
    years = ["2023", "2022", "2021"]
    form_groups = ["Annual Reports","Quarterly Reports","Insider Transactions","8-K Related","Registration Statements","Comment Letters"]
    
    base_url = f"https://api.nasdaq.com/api/company/{symbol.upper().replace("-", "%25sl%25")}/sec-filings?sortColumn=filed&sortOrder=desc"
        
    filings = list_sec_filings(symbol)
    for year in years:
        base_url += f"&Year={year}"
        for form_group in form_groups:
            base_url += f"&FormGroup={form_group}"
        
            print(f"Fetching data from: {base_url}")

            response = requests.get(base_url, timeout=15, headers={
                                    "User-Agent": "Mozilla/5.0"})
            body = response.json()

            if body["status"]["rCode"] != 200:
                raise Exception(f"Failed to fetch data for {symbol} - {body['status']['developerMessage']}")

            data = body["data"]["rows"]
            
            if len(data) <=0:
                continue
            
            for filing in data:
                filings.append(filing)

    return filings

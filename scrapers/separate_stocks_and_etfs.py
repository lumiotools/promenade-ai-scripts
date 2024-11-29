import csv

def separate_stocks_and_etfs(input_file):
    companies = []
    etfs = []

    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader) 
        
        for row in reader:
            symbol, description = row
            
            if 'ETF' in description:
                etfs.append(row)
            else:
                companies.append(row)
    
    with open('./data/companies.csv', 'w', newline='') as companiesfile:
        writer = csv.writer(companiesfile)
        writer.writerow(headers)
        writer.writerows(companies)
    
    with open('./data/etfs.csv', 'w', newline='') as etfsfile:
        writer = csv.writer(etfsfile)
        writer.writerow(headers)
        writer.writerows(etfs)
    
    print(f"Separation complete:")
    print(f"Companies: {len(companies)} rows")
    print(f"ETFs: {len(etfs)} rows")

separate_stocks_and_etfs('./data/stocks.csv')
import pandas as pd
import math

def split_csv_into_three_parts(input_file):

    df = pd.read_csv(input_file)
    
    total_rows = len(df)
    rows_per_part = math.ceil(total_rows / 3)
    
    part1 = df.iloc[:rows_per_part]
    part2 = df.iloc[rows_per_part:rows_per_part*2]
    part3 = df.iloc[rows_per_part*2:]
    
    part1.to_csv('companies_part1.csv', index=False)
    part2.to_csv('companies_part2.csv', index=False)
    part3.to_csv('companies_part3.csv', index=False)
    
    print(f"Total items in original file: {total_rows}")
    print(f"\nPart 1 details:")
    print(f"Rows: {len(part1)}")
    print("Items:", list(part1['Symbol']))
    
    print(f"\nPart 2 details:")
    print(f"Rows: {len(part2)}")
    print("Items:", list(part2['Symbol']))
    
    print(f"\nPart 3 details:")
    print(f"Rows: {len(part3)}")
    print("Items:", list(part3['Symbol']))

split_csv_into_three_parts('./data/companies.csv')
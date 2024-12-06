import pandas as pd
import math

def split_csv_into_three_parts(input_file):

    df = pd.read_csv(input_file)
    
    total_rows = len(df)
    rows_per_part = math.ceil(total_rows / 5)
    
    part1 = df.iloc[:rows_per_part]
    part2 = df.iloc[rows_per_part:rows_per_part*2]
    part3 = df.iloc[rows_per_part*2:rows_per_part*3]
    part4 = df.iloc[rows_per_part*3:rows_per_part*4]
    part5 = df.iloc[rows_per_part*4:]
    
    part1.to_csv('data/companies_part3.1.csv', index=False)
    part2.to_csv('data/companies_part3.2.csv', index=False)
    part3.to_csv('data/companies_part3.3.csv', index=False)
    part4.to_csv('data/companies_part3.4.csv', index=False)
    part5.to_csv('data/companies_part3.5.csv', index=False)
    
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
    
    print(f"\nPart 4 details:")
    print(f"Rows: {len(part4)}")
    print("Items:", list(part4['Symbol']))
    
    print(f"\nPart 5 details:")
    print(f"Rows: {len(part5)}")
    print("Items:", list(part5['Symbol']))

split_csv_into_three_parts('./data/companies_part3.csv')
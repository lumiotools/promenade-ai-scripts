from datetime import datetime
import pandas as pd
import os

df  = pd.read_csv('data/companies_part3.3.csv')
symbols = df['Symbol'].values

print(datetime.now().strftime('%I:%M:%S'), " - ", len([s for s in symbols if os.path.exists(f'output/{s}.json')]))
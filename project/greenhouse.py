import os
import pandas as pd
import sqlite3
from kaggle.api.kaggle_api_extended import KaggleApi

api_kaggle = KaggleApi()
api_kaggle.authenticate()

data_address = 'konradb/greenhouse-gas-giants'

directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'konradb')
csv = api_kaggle.dataset_download_files(data_address, path=data_address, unzip=True)
file = os.path.join(directory, 'emissions_high_granularity.csv')

path = "../data/greenhouse.db"

pd_csv = pd.read_csv(file)
os.makedirs(os.path.dirname(path), exist_ok=True)
connection = sqlite3.connect(path)
pd_csv.to_sql("high", connection, if_exists="replace", index=False)
connection.close()
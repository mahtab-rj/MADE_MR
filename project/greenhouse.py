import os
import pandas as pd
import sqlite3
from kaggle.api.kaggle_api_extended import KaggleApi

api_kaggle = KaggleApi()
api_kaggle.authenticate()

data_address = 'imtkaggleteam/co-and-greenhouse-gas-emissions'
data_address2 = 'subhamjain/temperature-of-all-countries-19952020'

api_kaggle.dataset_download_files(data_address, path='./data', unzip=True)
api_kaggle.dataset_download_files(data_address2, path='./data2', unzip=True)

directory = [x for x in os.listdir('./data') if x.endswith('.csv')]
directory2 = [x for x in os.listdir('./data2') if x.endswith('.csv')]
green = pd.read_csv(os.path.join('./data',directory[1]))
temperature = pd.read_csv(os.path.join('./data2',directory2[0]))

path = "../data/greenhouse.db"
connection = sqlite3.connect(path)

green.to_sql('greenhouse', connection, if_exists="replace", index=False)
temperature.to_sql('temperature_cities', connection, if_exists="replace", index=False)

connection.commit()
connection.close()
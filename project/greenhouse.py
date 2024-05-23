import os
import pandas as pd
import sqlite3
from kaggle.api.kaggle_api_extended import KaggleApi

api_kaggle = KaggleApi()
api_kaggle.authenticate()

data_address = 'konradb/greenhouse-gas-giants/'

directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'konradb/greenhouse-gas-giants')

file_list = os.listdir(directory)
csv = api_kaggle.dataset_download_files(data_address, path=data_address, unzip=True)
files_list = []
table_names = []
for file in file_list:
    if file[-4:] != ".pdf" :
        # print(file)
        files_list.append(os.path.join(directory, file))
        table_names.append(file[ : -4])
        # print(table_names)

path = "../data/greenhouse.db"
os.makedirs(os.path.dirname(path), exist_ok=True)
connection = sqlite3.connect(path)

for i in range(3): 
    pd_csv = pd.read_csv(files_list[i])
    pd_csv.to_sql(table_names[i], connection, if_exists="replace", index=False)


connection.close()
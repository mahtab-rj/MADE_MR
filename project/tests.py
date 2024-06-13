import os
import pandas as pd
import sqlite3
import pytest
from greenhouse import *


def test_data_download():
    assert os.path.exists('./data'), "Data folder does not exist."
    assert os.listdir('./data'), "Data folder is empty."
    assert os.path.exists('./data2'), "Data2 folder does not exist."
    assert os.listdir('./data2'), "Data2 folder is empty."


def test_data_cleaning():
    city_temperature = temperature
    city_temperature = city_temperature[city_temperature['AvgTemperature'] != -99]
    assert not city_temperature['AvgTemperature'].eq(-99).any(), "Data cleaning failed for AvgTemperature."

    city_temperature['Country'] = city_temperature['Country'].replace({'US': 'United States'})
    assert 'US' not in city_temperature['Country'].values, "Data cleaning failed for Country."

    city_temperature['AvgTemperature'] = (city_temperature['AvgTemperature'] - 32) * (5 / 9)
    assert city_temperature['AvgTemperature'].max() <= 100, "Temperature conversion failed."


def test_data_transformation():
    city_temperature = temperature
    annual_temp = city_temperature.groupby(['Year', 'Country']).agg({'AvgTemperature': 'mean'}).reset_index()
    assert 'Year' in annual_temp.columns, "Year column missing after transformation."
    assert 'Country' in annual_temp.columns, "Country column missing after transformation."
    assert 'AvgTemperature' in annual_temp.columns, "AvgTemperature column missing after transformation."


def test_data_merging():
    city_temperature = temperature
    co2_emissions = green
    annual_temp = city_temperature.groupby(['Year', 'Country']).agg({'AvgTemperature': 'mean'}).reset_index()
    co2_emissions = co2_emissions.rename(columns={'Entity': 'Country', 'Annual CO₂ emissions': 'Annual CO2 emissions'})

    merged_data = pd.merge(annual_temp, co2_emissions, on=['Year', 'Country'])
    assert 'AvgTemperature' in merged_data.columns, "AvgTemperature column missing in merged data."
    assert 'Annual CO2 emissions' in merged_data.columns, "Annual CO2 emissions column missing in merged data."


def test_database_storage():
    path = "../data/merged_data.db"
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='merged_data';")
    assert cursor.fetchone(), "Database table 'merged_data' does not exist."

    cursor.execute("SELECT * FROM merged_data;")
    assert cursor.fetchone(), "Database table 'merged_data' is empty."
    conn.close()


if __name__ == '__main__':
    test_data_download()
    test_data_cleaning()
    test_data_transformation()
    test_data_merging()
    test_database_storage()

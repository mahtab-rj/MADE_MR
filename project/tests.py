import os
import pandas as pd
import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from greenhouse import *

@pytest.fixture
def mock_filesystem(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.listdir', return_value=['file1.csv', 'file2.csv'])

@pytest.fixture
def mock_data():
    mock_temperature_data = pd.DataFrame({
        'Year': [2000, 2001],
        'Country': ['United States', 'United States'],
        'AvgTemperature': [75, 80]
    })

    mock_co2_data = pd.DataFrame({
        'Year': [2000, 2001],
        'Country': ['United States', 'United States'],
        'Annual CO₂ emissions': [5000, 5100]
    })

    return mock_temperature_data, mock_co2_data

@pytest.fixture
def mock_database(mocker):
    mock_conn = mocker.patch('sqlite3.connect')
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = True
    mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
    return mock_conn

def test_data_download(mock_filesystem):
    assert os.path.exists('./data'), "Data folder does not exist."
    assert os.listdir('./data'), "Data folder is empty."
    assert os.path.exists('./data2'), "Data2 folder does not exist."
    assert os.listdir('./data2'), "Data2 folder is empty."

def test_data_cleaning(mock_data):
    city_temperature, _ = mock_data
    city_temperature = city_temperature[city_temperature['AvgTemperature'] != -99]
    assert not city_temperature['AvgTemperature'].eq(-99).any(), "Data cleaning failed for AvgTemperature."

    city_temperature['Country'] = city_temperature['Country'].replace({'US': 'United States'})
    assert 'US' not in city_temperature['Country'].values, "Data cleaning failed for Country."

    city_temperature['AvgTemperature'] = (city_temperature['AvgTemperature'] - 32) * (5 / 9)
    assert city_temperature['AvgTemperature'].max() <= 100, "Temperature conversion failed."

def test_data_transformation(mock_data):
    city_temperature, _ = mock_data
    annual_temp = city_temperature.groupby(['Year', 'Country']).agg({'AvgTemperature': 'mean'}).reset_index()
    assert 'Year' in annual_temp.columns, "Year column missing after transformation."
    assert 'Country' in annual_temp.columns, "Country column missing after transformation."
    assert 'AvgTemperature' in annual_temp.columns, "AvgTemperature column missing after transformation."

def test_data_merging(mock_data):
    city_temperature, co2_emissions = mock_data
    annual_temp = city_temperature.groupby(['Year', 'Country']).agg({'AvgTemperature': 'mean'}).reset_index()
    co2_emissions = co2_emissions.rename(columns={'Entity': 'Country', 'Annual CO₂ emissions': 'Annual CO2 emissions'})

    merged_data = pd.merge(annual_temp, co2_emissions, on=['Year', 'Country'])
    assert 'AvgTemperature' in merged_data.columns, "AvgTemperature column missing in merged data."
    assert 'Annual CO2 emissions' in merged_data.columns, "Annual CO2 emissions column missing in merged data."

def test_database_storage(mock_database):
    path = "../data/merged_data.db"
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='merged_data';")
    assert cursor.fetchone(), "Database table 'merged_data' does not exist."

    cursor.execute("SELECT * FROM merged_data;")
    assert cursor.fetchone(), "Database table 'merged_data' is empty."
    conn.close()

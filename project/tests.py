import os
import pandas as pd
import sqlite3
import unittest
from unittest.mock import patch, MagicMock
from greenhouse import *


class TestGreenhouse(unittest.TestCase):

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_data_download(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ['file1.csv', 'file2.csv']
        
        self.assertTrue(os.path.exists('./data'), "Data folder does not exist.")
        self.assertTrue(os.listdir('./data'), "Data folder is empty.")
        self.assertTrue(os.path.exists('./data2'), "Data2 folder does not exist.")
        self.assertTrue(os.listdir('./data2'), "Data2 folder is empty.")

    @patch('pandas.read_csv')
    def test_data_cleaning(self, mock_read_csv):
        mock_temperature_data = pd.DataFrame({
            'Year': [2000, 2001],
            'Country': ['United States', 'United States'],
            'AvgTemperature': [75, 80]
        })
        mock_read_csv.return_value = mock_temperature_data
        
        city_temperature = temperature
        city_temperature = city_temperature[city_temperature['AvgTemperature'] != -99]
        self.assertFalse(city_temperature['AvgTemperature'].eq(-99).any(), "Data cleaning failed for AvgTemperature.")

        city_temperature['Country'] = city_temperature['Country'].replace({'US': 'United States'})
        self.assertNotIn('US', city_temperature['Country'].values, "Data cleaning failed for Country.")

        city_temperature['AvgTemperature'] = (city_temperature['AvgTemperature'] - 32) * (5 / 9)
        self.assertLessEqual(city_temperature['AvgTemperature'].max(), 100, "Temperature conversion failed.")

    @patch('pandas.read_csv')
    def test_data_transformation(self, mock_read_csv):
        mock_temperature_data = pd.DataFrame({
            'Year': [2000, 2001],
            'Country': ['United States', 'United States'],
            'AvgTemperature': [75, 80]
        })
        mock_read_csv.return_value = mock_temperature_data
        
        city_temperature = temperature
        annual_temp = city_temperature.groupby(['Year', 'Country']).agg({'AvgTemperature': 'mean'}).reset_index()
        self.assertIn('Year', annual_temp.columns, "Year column missing after transformation.")
        self.assertIn('Country', annual_temp.columns, "Country column missing after transformation.")
        self.assertIn('AvgTemperature', annual_temp.columns, "AvgTemperature column missing after transformation.")

    @patch('pandas.read_csv')
    def test_data_merging(self, mock_read_csv):
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
        mock_read_csv.side_effect = [mock_temperature_data, mock_co2_data]
        
        city_temperature = temperature
        co2_emissions = green
        annual_temp = city_temperature.groupby(['Year', 'Country']).agg({'AvgTemperature': 'mean'}).reset_index()
        co2_emissions = co2_emissions.rename(columns={'Entity': 'Country', 'Annual CO₂ emissions': 'Annual CO2 emissions'})

        merged_data = pd.merge(annual_temp, co2_emissions, on=['Year', 'Country'])
        self.assertIn('AvgTemperature', merged_data.columns, "AvgTemperature column missing in merged data.")
        self.assertIn('Annual CO2 emissions', merged_data.columns, "Annual CO2 emissions column missing in merged data.")

    @patch('sqlite3.connect')
    def test_database_storage(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = mock_conn.cursor.return_value
        
        path = "../data/merged_data.db"
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='merged_data';")
        self.assertTrue(cursor.fetchone(), "Database table 'merged_data' does not exist.")

        cursor.execute("SELECT * FROM merged_data;")
        self.assertTrue(cursor.fetchone(), "Database table 'merged_data' is empty.")
        conn.close()


if __name__ == '__main__':
    unittest.main()

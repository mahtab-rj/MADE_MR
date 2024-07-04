import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress

# Load the merged dataset from the database
path = os.path.abspath("./data/merged_data.db")
conn = sqlite3.connect(path)
merged_data = pd.read_sql('SELECT * FROM merged_data', conn)
conn.close()

# Exploratory Data Analysis (EDA)
print(merged_data.info())
print(merged_data.describe())
print(merged_data.head())

# Visualizations

# 1. Global average temperature trend over the years
plt.figure(figsize=(10, 6))
sns.lineplot(data=merged_data, x='Year', y='AvgTemperature', ci=None)
plt.title('Global Average Temperature Trend Over the Years')
plt.xlabel('Year')
plt.ylabel('Average Temperature (°C)')
plt.show()

# 2. Global CO2 emissions trend over the years
plt.figure(figsize=(10, 6))
sns.lineplot(data=merged_data, x='Year', y='Annual CO2 emissions', ci=None)
plt.title('Global CO2 Emissions Trend Over the Years')
plt.xlabel('Year')
plt.ylabel('Annual CO2 Emissions (million tonnes)')
plt.show()

# 3. Scatter plot of CO2 emissions vs. average temperature
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_data, x='Annual CO2 emissions', y='AvgTemperature')
plt.title('CO2 Emissions vs. Average Temperature')
plt.xlabel('Annual CO2 Emissions (million tonnes)')
plt.ylabel('Average Temperature (°C)')
plt.show()

# Statistical Analysis

# 4. Calculate the correlation between CO2 emissions and average temperature
correlation = merged_data[['Annual CO2 emissions', 'AvgTemperature']].corr()
print(f"Correlation between CO2 emissions and average temperature:\n{correlation}")

# 5. Perform linear regression analysis
slope, intercept, r_value, p_value, std_err = linregress(merged_data['Annual CO2 emissions'], merged_data['AvgTemperature'])
print(f"Linear regression results:\nSlope: {slope}\nIntercept: {intercept}\nR-squared: {r_value**2}\nP-value: {p_value}")

# 6. Plot the linear regression line
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_data, x='Annual CO2 emissions', y='AvgTemperature')
plt.plot(merged_data['Annual CO2 emissions'], intercept + slope*merged_data['Annual CO2 emissions'], color='red')
plt.title('CO2 Emissions vs. Average Temperature with Regression Line')
plt.xlabel('Annual CO2 Emissions (million tonnes)')
plt.ylabel('Average Temperature (°C)')
plt.show()
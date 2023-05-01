# Imports
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from datetime import datetime, timedelta
import streamlit as st
import seaborn as sns
import plotly.express as px

# Personal Acess Token Input
OURA_ACCESS_TOKEN = "JE6B5MLHNNWJ35XDOV75EGRZKK6JRM4I"

# Define a function to get Oura data:
def get_oura_data(endpoint, start_date=None, end_date=None):
    base_url = "https://api.ouraring.com/v1/"
    headers = {
        "Authorization": f"Bearer {OURA_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    params = {}
    if start_date:
        params["start"] = start_date
    if end_date:
        params["end"] = end_date

    response = requests.get(base_url + endpoint, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Functions to get sleep, activity, and readiness data
def get_sleep_data(start_date=None, end_date=None):
    sleep_data = get_oura_data("sleep", start_date, end_date)
    sleep_df = pd.DataFrame(sleep_data["sleep"])
    sleep_df["summary_date"] = pd.to_datetime(sleep_df["summary_date"])
    return sleep_df

def get_activity_data(start_date=None, end_date=None):
    activity_data = get_oura_data("activity", start_date, end_date)
    activity_df = pd.DataFrame(activity_data["activity"])
    activity_df["summary_date"] = pd.to_datetime(activity_df["summary_date"])
    return activity_df

def get_readiness_data(start_date=None, end_date=None):
    readiness_data = get_oura_data("readiness", start_date, end_date)
    readiness_df = pd.DataFrame(readiness_data["readiness"])
    readiness_df["summary_date"] = pd.to_datetime(readiness_df["summary_date"])
    return readiness_df

# Sleep, activitiy, readiness dataframes
sleep_df = get_sleep_data(start_date="2023-04-17", end_date="2023-4-23")

activity_df = get_activity_data(start_date="2023-04-17", end_date="2023-4-23")

readiness_df = get_readiness_data(start_date="2023-04-17", end_date="2023-4-23")

# Merge data frames
merged_df = sleep_df.merge(activity_df, on="summary_date", suffixes=("_sleep", "_activity"))
merged_df = merged_df.merge(readiness_df, on="summary_date", suffixes=("_merged", "_readiness"))

print(merged_df.head())

# My Hypothesis (H1): There is a positive correlation between the activity level during the day and sleep efficiency at night.

# Null Hypothesis (H0): There is no correlation between the activity level during the day and sleep efficiency at night.

# Visualize relationship between daily movement and sleep efficiency

# The daily movement metric in Oura is caculcated based on a combination of the number of steps taken, the intensity of the activity, and the duration of the activity.

plt.figure(figsize=(10, 6))
plt.scatter(merged_df["daily_movement"], merged_df["efficiency"])
plt.xlabel("Daily Movement")
plt.ylabel("Sleep Efficiency")
plt.title("Daily Movement vs Sleep Efficiency")
plt.show()

# Calculate correlation

# A positive correlation (closer to 1) = higher activity levels are associated with better sleep efficiency


# A negative correlation (closer to -1) = higher activity levels are associated with worse sleepe efficiency


# 0 or close to 0 = little or no relationship between activity level and sleep efficiency

correlation = merged_df["daily_movement"].corr(merged_df["efficiency"])
print(f"Correlation between daily movement and sleep efficiency: {correlation:.2f}")
# Correlation between daily movement and sleep efficiency: -0.35

correlation_coefficient, p_value = pearsonr(merged_df["daily_movement"], merged_df["efficiency"])
print(f"Correlation coefficient: {correlation_coefficient:.2f}")
print(f"P-value: {p_value:.5f}")
# Correlation coefficient: -0.35
# P-value: 0.43972

# Since the p-value is greater than 0.05, I can't reject the null hypothesis. This means that there isn't a significant correlation between daily movement and sleep efficiency based on the data. In other words, the data does not provide strong evidence to support the hypothesis that higher activity levels during the day are associated with better sleep efficiency at night.

# Analyze average sleep duration
average_sleep_duration = sleep_df["duration"].mean()
print(f"Average sleep duration: {average_sleep_duration} seconds")
# Average sleep duration: 32717.14285714286 seconds

# Convert to hours
average_sleep_duration = sleep_df["duration"].mean()
average_sleep_duration_hours = average_sleep_duration / 3600
print(f"Average sleep duration: {average_sleep_duration_hours} hours")
# Average sleep duration: 9.088095238095239 hours

# Analyze average sleep efficiency
average_sleep_efficiency = sleep_df["efficiency"].mean()
print(f"Average sleep efficiency: {average_sleep_efficiency}%")
# Average sleep efficiency: 87.0%

# Sleep Efficiency vs. Readiness Score:

# Oura gives a Readiness score each day which is a holistic measure of the body's preparedness for mental and physical performance based on:
# Heart rate patterns, body temperature, respiratory rate, sleep, and the previous day's mental/physical strain.

# My Hypothesis (H1) is that readiness score increases when sleep efficiency goes up.

# Null Hypothesis (H0): There is no correlation between sleep efficiency and readiness scores.

x = merged_df["efficiency"]
y = merged_df["score"]

# Calculate the linear regression line
slope, intercept = np.polyfit(x, y, 1)
trendline = slope * x + intercept

plt.scatter(x, y)
plt.plot(x, trendline, color='red', linewidth=2)

plt.xlabel("Sleep Efficiency")
plt.ylabel("Readiness Score")
plt.title("Sleep Efficiency vs Readiness Score")
plt.show()

# Calculate the correlation coefficient and the p-value to see if the correlation is statistically significant:

# (If the p-value is less than 0.05, it indicates that the correlation is significant, reject the null hypothesis. 

# If the p-value is greater than or equal to 0.05, reject the null hypothesis)

correlation = merged_df["efficiency"].corr(merged_df["score"])
print(f"Correlation between sleep efficiency and readiness scores: {correlation:.2f}")

from scipy.stats import pearsonr

correlation_coefficient, p_value = pearsonr(merged_df["efficiency"], merged_df["score"])
print(f"Correlation coefficient: {correlation_coefficient:.2f}")
print(f"P-value: {p_value:.5f}")
# Correlation between sleep efficiency and readiness scores: 0.86
# Correlation coefficient: 0.86
# P-value: 0.01343

# These results indicate that there is a strong positive correlation between sleep efficiency and readiness scores, with a correlation coefficient of 0.86. This means that when sleep efficiency increases, readiness scores also tend to increase, and vice versa.

# The p-value of 0.01343 is less than the commonly used significance level of 0.05, which suggests that the observed correlation is statistically significant.

# Therefore, the null hypothesis can be rejected.

# Part 2

# Extract Heart Rate and Temperature Data from Sleep and Readiness Data

heart_rate_df = sleep_df[["summary_date", "hr_lowest", "hr_average"]]
temperature_df = readiness_df[["summary_date", "score_temperature"]]

# Combine data to visualze in Streamlit

# Sleep data visualization
st.title("Oura Data Visualization")

st.header("Sleep Data")
st.subheader("Sleep Stages (REM, Deep, Light)")
sleep_df_long = pd.melt(sleep_df, id_vars=['summary_date'], value_vars=['rem', 'deep', 'light'])
fig = px.bar(sleep_df_long, x='summary_date', y='value', color='variable', text='value', labels={'value':'Duration (s)'})
fig.update_layout(showlegend=True)
st.plotly_chart(fig)

# Activity data visualization
st.header("Activity Data")
st.subheader("Daily Movement")
fig = px.line(activity_df, x='summary_date', y='daily_movement', labels={'daily_movement':'Daily Movement'})
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

# Readiness data visualization
st.header("Readiness Data")
st.subheader("Readiness Score")
fig = px.line(readiness_df, x='summary_date', y='score', labels={'score':'Readiness Score'})
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

# Heart rate data visualization
st.header("Heart Rate Data")
st.subheader("Lowest and Average Heart Rate")
heart_rate_df = sleep_df[["summary_date", "hr_lowest", "hr_average"]]
heart_rate_df_long = pd.melt(heart_rate_df, id_vars=['summary_date'], value_vars=['hr_lowest', 'hr_average'])
fig = px.line(heart_rate_df_long, x='summary_date', y='value', color='variable', labels={'value':'Heart Rate (bpm)'})
fig.update_layout(showlegend=True)
st.plotly_chart(fig)

# Temperature data visualization
st.header("Temperature Data")
st.subheader("Temperature Deviation Score")
fig = px.line(temperature_df, x='summary_date', y='score_temperature', labels={'score_temperature':'Temperature Deviation'})
fig.update_layout(showlegend=False)
st.plotly_chart(fig)


# Create new environment: python -m venv myenv
# Activate the environment: myenv\Scripts\activate
# Run streamlit: python -m streamlit run "c:/Users/kevin/OneDrive/Desktop/Coding Temple/Capstone/Oura/Oura_Ring_Analysis_Final.py"
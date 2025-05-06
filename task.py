import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# File to store tasks
DATA_FILE = 'tasks.xlsx'

# Function to clean and ensure correct datatypes
def clean_task_dataframe(df):
    """
    Ensure correct datatypes and handle missing/invalid values.
    """
    # Ensure expected columns exist
    expected_columns = ['task_name', 'start_date', 'duration_days', 'expiry_date', 'prompt_date']
    for col in expected_columns:
        if col not in df.columns:
            df[col] = pd.NA

    # Convert date columns to datetime
    date_cols = ['start_date', 'expiry_date', 'prompt_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Ensure duration_days is numeric
    df['duration_days'] = pd.to_numeric(df['duration_days'], errors='coerce').fillna(0)

    # Fill missing task names with empty string
    df['task_name'] = df['task_name'].fillna('')

    return df

# Load or initialize data
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
    df = clean_task_dataframe(df)
else:
    df = pd.DataFrame(columns=['task_name', 'start_date', 'duration_days', 'expiry_date', 'prompt_date'])

st.title("📝 Task Tracker with Expiry Alerts")

# Input form
with st.form("task_form"):
    task_name = st.text_input("Task Name")
    start_date = st.date_input("Start Date", datetime.today())
    duration_days = st.number_input("Duration (days)", min_value=1, value=7)
    submitted = st.form_submit_button("Add Task")

    if submitted:
        expiry_date = start_date + timedelta(days=duration_days)
        prompt_date = expiry_date - timedelta(days=3)
        new_entry = pd.DataFrame({
            'task_name': [task_name],
            'start_date': [start_date],
            'duration_days': [duration_days],
            'expiry_date': [expiry_date],
            'prompt_date': [prompt_date]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success(f"Task '{task_name}' added!")

# Check for expired tasks
today = datetime.now()

# Ensure expiry_date column is datetime
df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce')

# Identify expired tasks
df['expired'] = df['expiry_date'] < today

# Show tasks table
st.subheader("📋 All Tasks")
st.dataframe(df[['task_name', 'start_date', 'duration_days', 'expiry_date', 'prompt_date', 'expired']])

# Show expired tasks
if df['expired'].any():
    st.subheader("⚠️ Expired Tasks")
    st.dataframe(df[df['expired']][['task_name', 'start_date', 'expiry_date']])
else:
    st.success("✅ No expired tasks.")

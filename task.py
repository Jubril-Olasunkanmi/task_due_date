import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# File to store tasks
DATA_FILE = 'tasks.xlsx'

# Load or initialize data
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
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
df['expired'] = df['expiry_date'] < today

# Show tasks table
st.subheader("📋 All Tasks")
st.dataframe(df)

# Show expired tasks
if df['expired'].any():
    st.subheader("⚠️ Expired Tasks")
    st.dataframe(df[df['expired']])
else:
    st.success("✅ No expired tasks.")


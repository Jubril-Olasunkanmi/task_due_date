import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe

# --- Google Sheets Setup ---
SHEET_ID = '1EZEkGW-IcItCsDsy3nUO9K1HWeqYfONsp88mvXaxbQE'
SHEET_NAME = 'Sheet1'

# Connect to Google Sheets
gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.worksheet(SHEET_NAME)

# Load data from Google Sheet
def load_data():
    df = get_as_dataframe(worksheet, evaluate_formulas=True, dtype=str)
    df = df.dropna(how='all')  # drop empty rows
    expected_cols = ['scheduler_name', 'scheduler_email', 'task_name', 'start_date', 'duration_days', 'expiry_date', 'prompt_date', 'expired']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ''
    return df[expected_cols]  # reorder columns

# Save data to Google Sheet (append new row)
def append_data(new_entry):
    existing_df = load_data()
    combined_df = pd.concat([existing_df, new_entry], ignore_index=True)
    worksheet.clear()
    set_with_dataframe(worksheet, combined_df)

# --- Streamlit App ---
st.title("📝 Task Tracker")

df = load_data()

# Input form
with st.form("task_form"):
    scheduler_name = st.text_input("Your Name (Scheduler)")
    scheduler_email = st.text_input("Your Email (for alerts)")
    task_name = st.text_input("Task Name")
    start_date = st.date_input("Start Date", datetime.today())
    duration_days = st.number_input("Duration (days)", min_value=1, value=7)
    submitted = st.form_submit_button("Add Task")

    if submitted:
        expiry_date = start_date + timedelta(days=duration_days)
        prompt_date = expiry_date - timedelta(days=1)  # adjust to 1 day before expiry
        new_entry = pd.DataFrame({
            'scheduler_name': [scheduler_name],
            'scheduler_email': [scheduler_email],
            'task_name': [task_name],
            'start_date': [start_date.strftime('%Y-%m-%d')],
            'duration_days': [duration_days],
            'expiry_date': [expiry_date.strftime('%Y-%m-%d')],
            'prompt_date': [prompt_date.strftime('%Y-%m-%d')],
            'expired': ['']  # initially empty; we’ll compute later
        })
        append_data(new_entry)
        st.success(f"Task '{task_name}' added by {scheduler_name}!")
        df = load_data()  # reload updated data

# Check for expired tasks
if not df.empty:
    df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce')
    today = datetime.now()
    df['expired'] = df['expiry_date'] < today

    # Prepare display DataFrame
    display_df = df.copy()
    date_cols = ['start_date', 'expiry_date', 'prompt_date']
    for col in date_cols:
        display_df[col] = pd.to_datetime(display_df[col], errors='coerce')
        display_df[col] = display_df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')

    st.subheader("📋 All Tasks")
    st.dataframe(display_df[['scheduler_name', 'scheduler_email', 'task_name', 'start_date', 'duration_days', 'expiry_date', 'prompt_date', 'expired']])

    # Show expired tasks
    if display_df['expired'].any():
        st.subheader("⚠️ Expired Tasks")
        st.dataframe(display_df[display_df['expired']][['scheduler_name', 'scheduler_email', 'task_name', 'start_date', 'expiry_date']])
    else:
        st.success("✅ No expired tasks.")
else:
    st.info("No tasks yet. Add a new task to get started!")

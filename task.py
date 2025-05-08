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
    if df.empty or 'task_name' not in df.columns:
        df = pd.DataFrame(columns=['task_name', 'start_date', 'duration_days', 'expiry_date', 'prompt_date'])
    else:
        df = df.dropna(subset=['task_name'])  # Drop empty rows
    return df

# Save data to Google Sheet (append mode)
def save_data(new_entry):
    existing_df = load_data()
    updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
    worksheet.clear()
    set_with_dataframe(worksheet, updated_df)

# --- Streamlit App ---
st.title("📝 Task Tracker with Google Sheets Backend")

df = load_data()

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
            'start_date': [start_date.strftime('%Y-%m-%d')],
            'duration_days': [duration_days],
            'expiry_date': [expiry_date.strftime('%Y-%m-%d')],
            'prompt_date': [prompt_date.strftime('%Y-%m-%d')]
        })
        save_data(new_entry)
        st.success(f"Task '{task_name}' added!")
        # Reload data after saving
        df = load_data()

# Check for expired tasks
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
st.dataframe(display_df[['task_name', 'start_date', 'duration_days', 'expiry_date', 'prompt_date', 'expired']])

# Show expired tasks
if display_df['expired'].any():
    st.subheader("⚠️ Expired Tasks")
    st.dataframe(display_df[display_df['expired']][['task_name', 'start_date', 'expiry_date']])
else:
    st.success("✅ No expired tasks.")

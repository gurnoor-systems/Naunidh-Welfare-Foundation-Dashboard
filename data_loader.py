import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

@st.cache_data(ttl=300)
def load_and_clean_data():
    """Fetches, merges, and cleans all foundation data from Google Sheets."""
    
    # 1. Connect to Database
    conn = st.connection("gsheets", type=GSheetsConnection)
    def fetch(url, sheet_name):
        return conn.read(spreadsheet=url, worksheet=sheet_name)

    try:
        # 2. Ingest Master & Directory Data
        df_master = fetch(st.secrets["ATTENDANCE_URL"], "Strike_Summary")
        df_master = df_master[~df_master["Department"].str.contains("Void", case=False, na=False)]
        
        df_dir = fetch(st.secrets["DIRECTORY_URL"], "Volunteer_Directory")
        df_dir_clean = df_dir[["Volunteer ID", "Contact (Email)"]] 
        
        df_master = pd.merge(df_master, df_dir_clean, on="Volunteer ID", how="left")
        
        # Clean Data Types
        for col in ["Total_Strikes", "Total_Events", "Present"]:
            df_master[col] = pd.to_numeric(df_master[col], errors="coerce").fillna(0)

        # 3. Ingest & Clean Drives Data
        df_drives = fetch(st.secrets["DRIVES_URL"], "Drive_log")
        df_drives.columns = df_drives.columns.str.strip()
        df_drives["Date"] = pd.to_datetime(df_drives["Date"], errors="coerce")
        df_drives = df_drives.dropna(subset=["Date"])
        df_drives["No. of Beneficiaries"] = pd.to_numeric(df_drives["No. of Beneficiaries"], errors="coerce").fillna(0)

        # 4. Ingest Education Data & Apply PII Filters
        df_edu = fetch(st.secrets["EDU_URL"], "Student Master File")
        df_edu.columns = df_edu.columns.str.strip()
        pii_columns = ["Parent/Guardian Contact", "Parents Name", "Address", "Background / Notes"]
        df_edu_safe = df_edu.drop(columns=pii_columns, errors='ignore').dropna(subset=["Student ID"])

        # 5. Ingest Survey & Log Data
        df_edu_survey = fetch(st.secrets["EDU_URL"], "Survey Department Log")
        df_edu_survey.columns = df_edu_survey.columns.str.strip()
        df_edu_survey["Date"] = pd.to_datetime(df_edu_survey["Date"], errors="coerce")
        df_edu_survey = df_edu_survey.dropna(subset=["Date"])
        df_edu_survey["Families Approached"] = pd.to_numeric(df_edu_survey["Families Approached"], errors="coerce").fillna(0)
        
        df_edu_log = fetch(st.secrets["EDU_URL"], "Educating Log")
        df_edu_log.columns = df_edu_log.columns.str.strip()
        df_edu_log["Date"] = pd.to_datetime(df_edu_log["Date"], errors="coerce")
        df_edu_log = df_edu_log.dropna(subset=["Date"])

        return df_master, df_drives, df_edu_safe, df_edu_survey, df_edu_log

    except Exception as e:
        st.error(f"Failed to load database: {e}")
        st.stop()
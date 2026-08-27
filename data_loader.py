import streamlit as st
import numpy as np
import pandas as pd
from streamlit_gsheets import GSheetsConnection

@st.cache_data(ttl=300)
def fetch_all_data():
    
    # 1. Connect to Database
    conn = st.connection("gsheets", type=GSheetsConnection)
    def fetch(url, sheet_name):
        return conn.read(spreadsheet=url, worksheet=sheet_name)

    try:

        # 2. Ingest Master & Directory Data
        df_master = fetch(st.secrets["ATTENDANCE_URL"], "Strike_Summary")
        df_master.columns = df_master.columns.str.strip() 
        
        df_master = df_master[~df_master["Department"].str.contains("Void", case=False, na=False)]
        
        df_dir = fetch(st.secrets["DIRECTORY_URL"], "Volunteer_Directory")
        df_dir.columns = df_dir.columns.str.strip()
        
        # Now it will safely find "Volunteer ID" without trailing spaces breaking it
        df_dir_clean = df_dir[["Volunteer ID", "Contact (Email)"]] 
        
        df_master = pd.merge(df_master, df_dir_clean, on="Volunteer ID", how="left")
        
        # Clean Data Types
        for col in ["Total_Strikes", "Total_Events", "Present"]:
            df_master[col] = pd.to_numeric(df_master[col], errors="coerce").fillna(0)

        # Calculate (Present / Total) * 100. If Total is 0, default to 0 to avoid division errors.
        import numpy as np
        df_master["Attendance_Rate"] = np.where(
            df_master["Total_Events"] > 0,
            (df_master["Present"] / df_master["Total_Events"]) * 100,
            0
        )

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
        
        # 1. Prepare Drives Data
        df_drives_clean = df_drives[["Drive ID", "Date", "Location", "Status", "No. of Beneficiaries"]].copy()
        df_drives_clean["Department"] = "Drives"
        df_drives_clean["Activity Type"] = df_drives["Type of Care Home"]
        df_drives_clean.rename(columns={"No. of Beneficiaries": "Impact_Count"}, inplace=True)

        # 2. Prepare Survey Data
        # Ensure 'Drive ID' and 'Location' exist, fill missing with placeholders if needed during transition
        if "Drive ID" not in df_edu_survey.columns: df_edu_survey["Drive ID"] = "N/A"
        if "Location" not in df_edu_survey.columns: df_edu_survey["Location"] = "Various"
        
        # Roll-up Surveys by Drive ID (Summing Families Approached)
        survey_rollup = df_edu_survey.groupby(["Drive ID", "Date", "Location"], as_index=False).agg(
            Impact_Count=("Families Approached", "sum")
        )
        survey_rollup["Department"] = "Education"
        survey_rollup["Activity Type"] = "Field Survey"
        survey_rollup["Status"] = "Completed"

        # 3. Prepare Educating Data
        if "Drive ID" not in df_edu_log.columns: df_edu_log["Drive ID"] = "N/A"
        if "Location" not in df_edu_log.columns: df_edu_log["Location"] = "Various"
        
        # Roll-up Education Sessions by Drive ID (Counting Active Educators)
        edu_rollup = df_edu_log.groupby(["Drive ID", "Date", "Location"], as_index=False).agg(
            Impact_Count=("Educator ID", "nunique") # Impact is the number of active teachers deployed
        )
        edu_rollup["Department"] = "Education"
        edu_rollup["Activity Type"] = "Teaching Session"
        edu_rollup["Status"] = "Completed"

        # 4. The Merge

        df_all_events = pd.concat([df_drives_clean, survey_rollup, edu_rollup], ignore_index=True)
        
        # Sort by most recent dates first
        df_all_events = df_all_events.sort_values(by="Date", ascending=False)

        # Return the new unified dataframe alongside the others
        return df_master, df_drives, df_edu_safe, df_edu_survey, df_edu_log, df_all_events
        
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        st.stop()
import streamlit as st
import pandas as pd
import datetime

# Import backend and views
from data_loader import load_and_clean_data
from views.exec_overview import render_exec_overview
from views.dept_ops import render_dept_ops
from views.hr_monitor import render_hr_monitor
from views.field_impact import render_field_impact

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="NWF Executive Dashboard", page_icon="logo.png", layout="wide")

col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.image("logo.png", use_container_width=True)
with col_title:
    st.title("Naunidh Welfare Foundation — Analytical Dashboard")
    st.caption("Live Operational Intelligence & Executive Impact Portal")
st.divider()

# ==========================================
# 2. LOAD & FILTER DATA
# ==========================================
df_master, df_drives, df_edu_safe, df_edu_survey, df_edu_log = load_and_clean_data()

st.sidebar.header("🎛️ Global Filters")
date_range = st.sidebar.date_input("📅 Filter by Date Range", (datetime.date(2026, 1, 6), datetime.datetime.now().date()))

departments = df_master["Department"].dropna().unique().tolist()
selected_depts = st.sidebar.multiselect("👥 Filter HR by Department", departments, default=departments)

# Apply Filters
df_master = df_master[df_master["Department"].isin(selected_depts)]

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_drives = df_drives[(df_drives["Date"] >= start_date) & (df_drives["Date"] <= end_date)]
    df_edu_survey = df_edu_survey[(df_edu_survey["Date"] >= start_date) & (df_edu_survey["Date"] <= end_date)]
    df_edu_log = df_edu_log[(df_edu_log["Date"] >= start_date) & (df_edu_log["Date"] <= end_date)]

# ==========================================
# 3. DASHBOARD ROUTING
# ==========================================
tab_exec, tab_dept, tab_hr, tab_impact = st.tabs([
    "📈 Executive Overview", 
    "👥 Department Operations", 
    "⚠️ HR Monitor",
    "🌍 Field Operations & Impact"
])

with tab_exec:
    render_exec_overview(df_master, df_drives, df_edu_safe, df_edu_survey)
    
with tab_dept:
    render_dept_ops(df_master)
    
with tab_hr:
    render_hr_monitor(df_master)
    
with tab_impact:
    render_field_impact(df_drives, df_edu_safe, df_edu_log, df_edu_survey)
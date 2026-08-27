import streamlit as st
import pandas as pd
import datetime
import hashlib
import hmac
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_and_clean_data
from views.exec_overview import render_exec_overview
from views.dept_ops import render_dept_ops
from views.hr_monitor import render_hr_monitor
from views.field_impact import render_field_impact

st.set_page_config(page_title="NWF Executive Dashboard", page_icon="logo.png", layout="wide")

st.markdown("""
    <style>
        /* Reduce top padding to fit more content on mobile screens */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Hide the default Streamlit top-right menu for a cleaner app-like feel */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

TIMEOUT_MINUTES = 15

def check_password():
    """Validates hashed password and enforces 15-minute idle timeout."""

    if "ADMIN_PASSWORD_HASH" not in st.secrets:
        st.error("🚨 Configuration Error: The application secrets are not properly configured on the server.")
        st.stop()

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if "last_activity" not in st.session_state:
        st.session_state["last_activity"] = datetime.datetime.now()

    if st.session_state["password_correct"]:
        now = datetime.datetime.now()
        if (now - st.session_state["last_activity"]).total_seconds() > (TIMEOUT_MINUTES * 60):
            st.session_state["password_correct"] = False
            st.warning("⏱️ Session expired due to inactivity. Please log in again.")
            return False
        else:
            # User is active; bump the timeout timer
            st.session_state["last_activity"] = now
            return True

    st.write("### 🔒 NWF Executive Dashboard Login")
    with st.form("login_form"):
        password = st.text_input("Enter Admin Password", type="password")
        submitted = st.form_submit_button("Log In")
        
        if submitted:
            # 1. Hash the user's input
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            # 2. Compare it securely against the stored hash
            if hmac.compare_digest(input_hash, st.secrets["ADMIN_PASSWORD_HASH"]):
                st.session_state["password_correct"] = True
                st.session_state["last_activity"] = datetime.datetime.now()
                st.rerun()
            else:
                st.error("😕 Incorrect password")
    
    return False

if not check_password():
    st.stop()

# ==========================================
# ISOLATED DASHBOARD FRAGMENT
# ==========================================
# By putting the main UI in a fragment, clicking a tab or changing a local 
# widget won't trigger the auth check or top-level script execution again.

@st.fragment
def render_main_dashboard():
    # ==========================================
    # LOGOUT BUTTON (Top of Sidebar)
    # ==========================================
    if st.sidebar.button("🚪 Log Out", width="stretch"):
        st.session_state["password_correct"] = False
        st.rerun() # Instantly re-runs the script, kicking them to the login screen
        
    st.sidebar.divider() # Visual separation from the filters
    
    # ==========================================
    # MAIN DASHBOARD UI
    # ==========================================
    col_logo, col_title = st.columns([1, 11])
    with col_logo:
        st.image("logo.png", width="stretch")
    with col_title:
        st.title("Naunidh Welfare Foundation — Dashboard")
        st.caption("Live Operational Intelligence & Executive Impact Portal")
    st.divider()

    # Data loads instantly from cache
    df_master, df_drives, df_edu_safe, df_edu_survey, df_edu_log, df_all_events = load_and_clean_data()

    st.sidebar.header("🎛️ Global Filters")
    date_range = st.sidebar.date_input("📅 Filter by Date Range", (datetime.date(2026, 1, 6), datetime.datetime.now().date()))
    
    departments = df_master["Department"].dropna().unique().tolist()
    selected_depts = st.sidebar.multiselect("👥 Filter HR by Department", departments, default=departments)

    df_master = df_master[df_master["Department"].isin(selected_depts)]

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_drives = df_drives[(df_drives["Date"] >= start_date) & (df_drives["Date"] <= end_date)]
        df_edu_survey = df_edu_survey[(df_edu_survey["Date"] >= start_date) & (df_edu_survey["Date"] <= end_date)]
        df_edu_log = df_edu_log[(df_edu_log["Date"] >= start_date) & (df_edu_log["Date"] <= end_date)]

    tab_exec, tab_dept, tab_hr, tab_impact = st.tabs([
        "📈 Executive Overview", "👥 Department Operations", "⚠️ HR Monitor", "🌍 Field Operations"
    ])

    with tab_exec:
        render_exec_overview(df_master, df_drives, df_edu_safe, df_edu_survey)
    with tab_dept:
        render_dept_ops(df_master)
    with tab_hr:
        render_hr_monitor(df_master)
    with tab_impact:
        render_field_impact(df_drives, df_edu_safe, df_edu_log, df_edu_survey, df_all_events)

# Call the fragment function
render_main_dashboard()
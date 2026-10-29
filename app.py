import streamlit as st
import pandas as pd
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import fetch_all_data
from access import require_login, touch_or_expire, scope_master, ROLE_TABS
from views.exec_overview import render_exec_overview
from views.dept_ops import render_dept_ops
from views.hr_monitor import render_hr_monitor
from views.field_impact import render_field_impact

st.set_page_config(page_title="NWF Dashboard", page_icon="logo.png", layout="wide")

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

REQUIRED_SECRETS = ["auth", "USERS", "ATTENDANCE_URL", "DIRECTORY_URL", "DRIVES_URL", "EDU_URL"]

def check_secrets():
    """Stop early if any required secret is missing (names go to server logs only)."""
    missing = [k for k in REQUIRED_SECRETS if k not in st.secrets]
    if missing:
        print(f"Missing secrets: {missing}", file=sys.stderr)
        st.error("🚨 Configuration Error: The application is not properly configured on the server.")
        st.stop()


check_secrets()
user = require_login()   # stops here unless the person is logged in AND on the allowlist

# ==========================================
# ISOLATED DASHBOARD FRAGMENT
# ==========================================
# By putting the main UI in a fragment, clicking a tab or changing a local 
# widget won't trigger the auth check or top-level script execution again.

@st.fragment
def render_main_dashboard(user):
    touch_or_expire()
    # ==========================================
    # LOGOUT BUTTON (Top of Sidebar)
    # ==========================================
    st.sidebar.caption(f"Signed in as {user['email']} ({user['role']})")
    if st.sidebar.button("🚪 Log Out", width="stretch"):
        st.logout()
        
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
    df_master, df_drives, df_edu_safe, df_edu_survey, df_edu_log, df_all_events = fetch_all_data()
    df_master = scope_master(df_master, user)   # HODs now only hold their own department

    st.sidebar.header("🎛️ Global Filters")
    date_range = st.sidebar.date_input("📅 Filter by Date Range", (datetime.date(2026, 1, 6), datetime.datetime.now().date()))
    
    departments = df_master["Department"].dropna().unique().tolist()
    selected_depts = st.sidebar.multiselect("👥 Filter HR by Department", departments, default=departments)

    df_master = df_master[df_master["Department"].isin(selected_depts)]

    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)  # end day fully included

        def in_range(df):
            return df[(df["Date"] >= start_date) & (df["Date"] < end_date)]

        df_drives = in_range(df_drives)
        df_edu_survey = in_range(df_edu_survey)
        df_edu_log = in_range(df_edu_log)
        df_all_events = in_range(df_all_events)   # was missing: the unified log ignored the filter
    else:
        st.sidebar.info("Select both a start and end date to apply the date filter.")

    TAB_LABELS = {
        "exec": "📈 Executive Overview",
        "dept": "👥 Department Operations",
        "hr": "⚠️ HR Monitor",
        "field": "🌍 Field Operations",
    }
    allowed = ROLE_TABS[user["role"]]
    tabs = st.tabs([TAB_LABELS[k] for k in allowed])

    for key, tab in zip(allowed, tabs):
        with tab:
            if key == "exec":
                render_exec_overview(df_master, df_drives, df_edu_safe, df_edu_survey)
            elif key == "dept":
                render_dept_ops(df_master)
            elif key == "hr":
                render_hr_monitor(df_master)
            elif key == "field":
                render_field_impact(df_drives, df_edu_safe, df_edu_log, df_edu_survey, df_all_events)

# Call the fragment function
render_main_dashboard(user)
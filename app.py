import streamlit as st
import pandas as pd
import datetime
import hashlib
import hmac
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import fetch_all_data
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

TIMEOUT_MINUTES = 15
REQUIRED_SECRETS = ["ADMIN_PASSWORD_HASH", "ATTENDANCE_URL", "DIRECTORY_URL", "DRIVES_URL", "EDU_URL"]


def check_secrets():
    """Stop early if any required secret is missing (names go to server logs only)."""
    missing = [k for k in REQUIRED_SECRETS if k not in st.secrets]
    if missing:
        print(f"Missing secrets: {missing}", file=sys.stderr)
        st.error("🚨 Configuration Error: The application is not properly configured on the server.")
        st.stop()


def expire_session():
    """Wipe the session and leave a flag so the login page can explain why."""
    st.session_state.clear()
    st.session_state["session_expired"] = True


def touch_or_expire():
    """Call from inside the fragment so every interaction refreshes or enforces the timeout."""
    now = datetime.datetime.now()
    last = st.session_state.get("last_activity")
    if (not st.session_state.get("password_correct")) or last is None \
            or (now - last).total_seconds() > TIMEOUT_MINUTES * 60:
        expire_session()
        st.rerun(scope="app")
    st.session_state["last_activity"] = now


def check_password():
    """Validates hashed password and enforces idle timeout."""
    check_secrets()

    st.session_state.setdefault("password_correct", False)
    st.session_state.setdefault("last_activity", datetime.datetime.now())

    if st.session_state["password_correct"]:
        now = datetime.datetime.now()
        if (now - st.session_state["last_activity"]).total_seconds() > TIMEOUT_MINUTES * 60:
            expire_session()          # fall through to the login form below
        else:
            st.session_state["last_activity"] = now
            return True

    if st.session_state.pop("session_expired", False):
        st.warning("⏱️ Session expired due to inactivity. Please log in again.")

    st.write("### 🔒 NWF Executive Dashboard Login")
    with st.form("login_form"):
        password = st.text_input("Enter Admin Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            input_hash = hashlib.sha256(password.encode()).hexdigest()
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
    touch_or_expire()
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
    df_master, df_drives, df_edu_safe, df_edu_survey, df_edu_log, df_all_events = fetch_all_data()

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
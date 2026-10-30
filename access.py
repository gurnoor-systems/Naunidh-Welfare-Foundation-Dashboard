import datetime
import re
import streamlit as st


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()

TIMEOUT_MINUTES = 15

# Which tabs each role may see
ROLE_TABS = {
    "leadership": ["exec", "dept", "hr", "students", "field"],
    "hr":         ["exec", "dept", "hr", "field"],
    "hod":        ["dept", "hr", "field"],
    "edu_hod":    ["dept", "hr", "students", "field"],
    "unit_head":  ["dept", "hr", "field"],
}
DEPT_SCOPED_ROLES = {"hod", "edu_hod", "unit_head"}   # see only their own department's volunteers
UNIT_SCOPED_ROLES = {"unit_head"}                     # ...and only their own unit within it
STUDENT_ROSTER_ROLES = {"leadership", "edu_hod"}      # the only roles that may see student names


def _load_users():
    users = {}
    for email, cfg in st.secrets.get("USERS", {}).items():
        users[str(email).strip().lower()] = {
            "role": cfg.get("role"),
            "department": cfg.get("department"),
            "unit": cfg.get("unit"),
        }
    return users


def require_login():
    """Returns the current user dict, or stops the app with a login/denied screen."""
    if not st.user.is_logged_in:
        st.write("### 🔒 NWF Internal Dashboard")
        st.caption("Sign in with your NWF Google account.")
        st.button("Log in with Google", on_click=st.login)
        st.stop()

    info = st.user.to_dict()
    email = str(info.get("email", "")).strip().lower()
    cfg = _load_users().get(email)

    if not info.get("email_verified", False) or cfg is None or cfg["role"] not in ROLE_TABS:
        st.error("Your account is not authorised for this dashboard. Contact the administrator.")
        st.button("Log out", on_click=st.logout)
        st.stop()

    if cfg["role"] in DEPT_SCOPED_ROLES and not cfg["department"]:
        st.error("Your account is missing a department assignment. Contact the administrator.")
        st.button("Log out", on_click=st.logout)
        st.stop()

    if cfg["role"] in UNIT_SCOPED_ROLES and not cfg["unit"]:
        st.error("Your account is missing a unit assignment. Contact the administrator.")
        st.button("Log out", on_click=st.logout)
        st.stop()

    return {
        "email": email,
        "name": info.get("name", email),
        "role": cfg["role"],
        "department": cfg["department"],
        "unit": cfg["unit"],
    }


def touch_or_expire():
    """Call at the top of the fragment: refreshes the idle timer or logs the user out."""
    now = datetime.datetime.now()
    last = st.session_state.get("last_activity", now)
    if (now - last).total_seconds() > TIMEOUT_MINUTES * 60:
        st.session_state.pop("last_activity", None)
        st.logout()
        st.stop()
    st.session_state["last_activity"] = now


def scope_master(df, user):
    """Row and column scoping for volunteer data, applied BEFORE any view sees it.
    A department of 'Strategic Operations Division' matches all its sub-departments;
    the full name 'Strategic Operations Division - PR Department' matches only that one.
    Unit heads are further limited to their exact unit."""
    if user["role"] in DEPT_SCOPED_ROLES:
        target = norm(user["department"])
        if not target:
            return df.iloc[0:0].copy()          # an empty department must never match everything
        df = df[df["Department"].map(norm).str.startswith(target)]
        df = df.drop(columns=["Contact (Email)"], errors="ignore")   # these roles don't get emails

    if user["role"] in UNIT_SCOPED_ROLES:
        unit = norm(user["unit"])
        if not unit or "Unit" not in df.columns:
            return df.iloc[0:0].copy()          # fail closed
        df = df[df["Unit"].map(norm) == unit]

    return df.copy()
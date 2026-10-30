import streamlit as st
import plotly.express as px

# Certificate policy (agreed with leadership)
MIN_ATTENDANCE = 70            # percent, inclusive
MAX_STRIKES = 3                # strikes must be BELOW this; 3 or more goes to review
DONE_STATUSES = {"processing", "issued"}   # already in the pipeline, not evaluated again

PROGRESS = st.column_config.ProgressColumn("Attendance Rate", format="%.0f%%", min_value=0, max_value=100)


def _review_reason(row):
    reasons = []
    if round(row["Attendance_Rate"], 2) < MIN_ATTENDANCE:
        reasons.append(f"Attendance below {MIN_ATTENDANCE}%")
    if row["Total_Strikes"] >= MAX_STRIKES:
        reasons.append(f"{int(row['Total_Strikes'])} strikes")
    return "; ".join(reasons)


def render_hr_monitor(df_master):
    st.subheader("Compliance & Certificate Oversight")

    if not df_master.empty:
        status_counts = df_master["SOP_Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig_hr = px.pie(
            status_counts,
            values="Count",
            names="Status",
            hole=0.4,
            color="Status",
            color_discrete_map={"GOOD STANDING": "#27AE60", "WARNING": "#F39C12", "STRIKE": "#C0392B"},
            template="plotly_dark",
            title="Foundation-Wide HR Health"
        )
        fig_hr.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_hr, width="stretch")

    st.write("### 🚨 High Risk / Warning List")
    df_warnings = df_master[df_master["Total_Strikes"] > 0].sort_values(by="Total_Strikes", ascending=False)

    if len(df_warnings) > 0:
        st.dataframe(
            df_warnings[["Volunteer ID", "Full_Name", "Department", "Total_Strikes", "SOP_Status"]],
            width="stretch",
            hide_index=True,
            column_config={
                "Total_Strikes": st.column_config.NumberColumn("⚠️ Strikes", format="%d"),
            }
        )
    else:
        st.success("No active strikes logged across the foundation!")

    # ---------------- Certificates ----------------
    st.write("### 🎓 Certificates")
    st.caption(
        f"Eligible: attendance of at least {MIN_ATTENDANCE}% and fewer than {MAX_STRIKES} strikes. "
        f"{MAX_STRIKES} or more strikes, or attendance below {MIN_ATTENDANCE}%, goes to review. "
        "Excused absences count against attendance."
    )

    df = df_master.copy()
    if "Certificate Status" not in df.columns:
        df["Certificate Status"] = ""
    df["Certificate Status"] = df["Certificate Status"].fillna("").astype(str).str.strip()
    status_key = df["Certificate Status"].str.lower()

    to_evaluate = df[~status_key.isin(DONE_STATUSES)]
    has_events = to_evaluate["Total_Events"] > 0
    passes = (to_evaluate["Attendance_Rate"].round(2) >= MIN_ATTENDANCE) & (to_evaluate["Total_Strikes"] < MAX_STRIKES)

    df_eligible = to_evaluate[has_events & passes]
    df_review = to_evaluate[has_events & ~passes].copy()
    df_no_events = to_evaluate[~has_events]

    if not df_review.empty:
        df_review["Review Reason"] = df_review.apply(_review_reason, axis=1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eligible", len(df_eligible))
    m2.metric("Under review", len(df_review))
    m3.metric("Processing", int((status_key == "processing").sum()))
    m4.metric("Issued", int((status_key == "issued").sum()))

    col_a, col_b = st.columns(2)
    with col_a:
        st.write("#### ✅ Eligible for certificate")
        if df_eligible.empty:
            st.info("No volunteers currently meet the certificate criteria.")
        else:
            st.dataframe(
                df_eligible[["Volunteer ID", "Full_Name", "Department", "Total_Events", "Attendance_Rate", "Certificate Status"]],
                width="stretch", hide_index=True,
                column_config={"Attendance_Rate": PROGRESS},
            )
    with col_b:
        st.write("#### 🔍 Under review")
        if df_review.empty:
            st.success("Nobody is currently flagged for review.")
        else:
            st.dataframe(
                df_review[["Volunteer ID", "Full_Name", "Department", "Attendance_Rate", "Total_Strikes", "Review Reason"]],
                width="stretch", hide_index=True,
                column_config={"Attendance_Rate": PROGRESS},
            )

    if not df_no_events.empty:
        st.caption(f"{len(df_no_events)} volunteer(s) have no events recorded yet and are not evaluated.")
import streamlit as st
import plotly.express as px

MIN_ATTENDANCE = 70      # same threshold as the certificate rule
MAX_STRIKES = 3          # 3 or more goes to review

BAND_COLORS = {
    "90% and above": "#2ECC71",
    "70–89%": "#3498DB",
    "Below 70%": "#E74C3C",
}


def _band(rate):
    if rate >= 90:
        return "90% and above"
    if rate >= MIN_ATTENDANCE:
        return "70–89%"
    return "Below 70%"


def render_dept_ops(df_master):
    st.subheader("Departmental Roster Explorer")
    st.write("Filter below to view a specific team.")

    departments = ["All Departments"] + list(df_master["Department"].dropna().unique())
    selected_dept = st.selectbox("Select Department:", departments)

    df_filtered = df_master if selected_dept == "All Departments" else df_master[df_master["Department"] == selected_dept]
    st.write(f"Showing **{len(df_filtered)}** team members in **{selected_dept}**:")

    if df_filtered.empty:
        st.info("No team members to show.")
        return

    d = df_filtered.copy()
    active = d[d["Total_Events"] > 0].copy()      # volunteers with no events yet aren't ranked

    # ----- Summary numbers -----
    avg_rate = active["Attendance_Rate"].mean() if not active.empty else 0
    below = int((active["Attendance_Rate"].round(2) < MIN_ATTENDANCE).sum())
    in_review = int((d["Total_Strikes"] >= MAX_STRIKES).sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Team size", len(d))
    k2.metric("Avg attendance", f"{avg_rate:.0f}%")
    k3.metric(f"Below {MIN_ATTENDANCE}%", below)
    k4.metric(f"{MAX_STRIKES}+ strikes", in_review)

    # ----- Ranked attendance chart -----
    if active.empty:
        st.info("No attendance recorded yet for this selection.")
    else:
        active["Band"] = active["Attendance_Rate"].round(2).map(_band)
        active = active.sort_values("Attendance_Rate", ascending=False)   # lowest ends up at the top

        fig = px.bar(
            active,
            x="Attendance_Rate",
            y="Full_Name",
            orientation="h",
            color="Band",
            color_discrete_map=BAND_COLORS,
            category_orders={"Band": list(BAND_COLORS)},
            hover_data={"Volunteer ID": True, "Total_Events": True, "Present": True,
                        "Total_Strikes": True, "SOP_Status": True,
                        "Attendance_Rate": ":.0f", "Full_Name": False, "Band": False},
            template="plotly_dark",
            title="Attendance by Volunteer (lowest first)",
        )
        fig.add_vline(x=MIN_ATTENDANCE, line_dash="dash", line_color="#ECF0F1",
                      annotation_text=f"{MIN_ATTENDANCE}% target", annotation_position="top")
        fig.update_xaxes(range=[0, 100], title="Attendance rate (%)")
        fig.update_yaxes(title="", categoryorder="array", categoryarray=list(active["Full_Name"]))
        fig.update_layout(
            height=max(320, 26 * len(active) + 120),
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, title=""),
        )
        st.plotly_chart(fig, width="stretch")

        if len(d) > len(active):
            st.caption(f"{len(d) - len(active)} volunteer(s) with no events yet are not shown in the chart.")

    # ----- Table -----
    wanted = ["Volunteer ID", "Full_Name", "Contact (Email)", "Department", "Total_Events",
              "Present", "Attendance_Rate", "SOP_Status"]
    st.dataframe(
        d[[c for c in wanted if c in d.columns]],
        width="stretch",
        hide_index=True,
        column_config={
            "Volunteer ID": st.column_config.TextColumn("ID", width="small"),
            "Full_Name": st.column_config.TextColumn("Volunteer Name", width="medium"),
            "Attendance_Rate": st.column_config.ProgressColumn("Attendance Rate", format="%.0f%%", min_value=0, max_value=100),
        },
    )
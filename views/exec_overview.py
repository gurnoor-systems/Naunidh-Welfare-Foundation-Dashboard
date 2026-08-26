import streamlit as st

def render_exec_overview(df_master, df_drives, df_edu_safe, df_edu_survey):
    st.write("### 🌍 Global Foundation Impact")
    st.caption("Aggregated community impact metrics across all active field operations.")
    
    total_beneficiaries = int(df_drives["No. of Beneficiaries"].sum())
    total_students = len(df_edu_safe)
    families_approached = int(df_edu_survey["Families Approached"].sum())
    total_impact = total_beneficiaries + total_students + families_approached
    total_volunteers = len(df_master)
    
    col_hero1, col_hero2 = st.columns(2)
    with col_hero1.container(border=True):
        st.metric("Total Community Members Impacted (Est.)", f"{total_impact} ❤️")
    with col_hero2.container(border=True):
        st.metric("Active Volunteers", f"{total_volunteers} 👥")
    
    col_exec1, col_exec2, col_exec3 = st.columns(3)
    with col_exec1.container(border=True):
        st.metric("Drive Beneficiaries", f"{total_beneficiaries} 🤝")
    with col_exec2.container(border=True):
        st.metric("Students Enrolled", f"{total_students} 🎓")
    with col_exec3.container(border=True):
        st.metric("Families Approached", f"{families_approached} 🏘️")
        
    st.divider()

    st.write("### 📈 Cumulative Impact Trajectory")
    st.caption("Month-over-month growth of community members directly supported.")
    if not df_drives.empty:
        timeline_df = df_drives.groupby("Date")["No. of Beneficiaries"].sum().reset_index()
        timeline_df = timeline_df.sort_values("Date")
        timeline_df["Cumulative Beneficiaries"] = timeline_df["No. of Beneficiaries"].cumsum()
        st.line_chart(timeline_df.set_index("Date")["Cumulative Beneficiaries"], color="#E74C3C", use_container_width=True)
    else:
        st.info("No field operations data available for the selected date range.")

    st.divider()
    st.write("### 🏢 Internal Operations Health")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1.container(border=True):
        st.write("#### Roster Breakdown")
        st.bar_chart(df_master["Department"].value_counts(), color="#2C3E50", use_container_width=True) 
    with col_chart2.container(border=True):
        st.write("#### Standing Status")
        st.bar_chart(df_master["SOP_Status"].value_counts(), color="#27AE60", use_container_width=True)
import streamlit as st

def render_field_impact(df_drives, df_edu_safe, df_edu_log, df_edu_survey):
    st.title("Field Operations & Community Impact")
    st.write("Real-time metrics from the Drives Department.")
    
    completed_drives = len(df_drives[df_drives["Status"] == "Completed"])
    total_beneficiaries = int(df_drives["No. of Beneficiaries"].sum())
    unique_locations = df_drives["Location"].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1.container(border=True):
        st.metric("Total Drives Executed", f"{completed_drives} 🚐")
    with col2.container(border=True):
        st.metric("Beneficiaries Impacted", f"{total_beneficiaries} 🤝")
    with col3.container(border=True):
        st.metric("Partner Locations", f"{unique_locations} 🏥")
        
    st.divider()
    
    st.write("### 📋 Recent Drive Logs")
    st.dataframe(
        df_drives[["Drive ID", "Date", "Location", "Type of Care Home", "Status", "No. of Beneficiaries"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Drive Date", format="MMM DD, YYYY"),
            "Status": st.column_config.TextColumn("Status"),
            "No. of Beneficiaries": st.column_config.NumberColumn("Beneficiaries", format="%d")
        }
    )

    st.write("---")
    st.write("### 📚 Education Department Operations")
    
    total_students = len(df_edu_safe)
    active_educators = df_edu_log["Educator ID"].nunique()
    families_approached = int(df_edu_survey["Families Approached"].sum())
    total_sessions = len(df_edu_log)
    
    col_edu1, col_edu2, col_edu3, col_edu4 = st.columns(4)
    with col_edu1.container(border=True):
        st.metric("Enrolled Students", f"{total_students} 🧑‍🎓")
    with col_edu2.container(border=True):
        st.metric("Active Educators", f"{active_educators} 🧑‍🏫")
    with col_edu3.container(border=True):
        st.metric("Families Approached", f"{families_approached} 🏘️")
    with col_edu4.container(border=True):
        st.metric("Teaching Sessions", f"{total_sessions} 📝")
        
    st.write("#### 🧑‍🎓 Anonymized Student Roster")
    st.caption("Privacy Notice: PII (Phone numbers, Parent Names, Addresses) are strictly masked at the database level and omitted from this portal.")
    
    st.dataframe(df_edu_safe, use_container_width=True, hide_index=True)
import streamlit as st
import plotly.express as px

def render_field_impact(df_drives, df_edu_safe, df_edu_log, df_edu_survey, df_all_events):
    st.title("Field Operations & Community Impact")
    
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
    
    if not df_drives.empty:
        loc_data = df_drives.groupby("Location")["No. of Beneficiaries"].sum().reset_index()
        fig_loc = px.bar(
            loc_data.sort_values("No. of Beneficiaries", ascending=False), 
            x="Location", 
            y="No. of Beneficiaries",
            template="plotly_dark",
            color_discrete_sequence=["#3498DB"],
            title="Total Beneficiaries by Partner Location"
        )
        st.plotly_chart(fig_loc, use_container_width=True)
    
    st.write("### 📋 Unified Foundation Operations Log")
    st.caption("A consolidated timeline of all field drives, surveys, and teaching sessions.")

    st.dataframe(
        df_all_events[["Drive ID", "Date", "Department", "Activity Type", "Location", "Impact_Count", "Status"]],
        width="stretch",
        hide_index=True,
        column_config={
            "Drive ID": st.column_config.TextColumn("Event ID", width="small"),
            "Date": st.column_config.DateColumn("Drive Date", format="MMM DD, YYYY"),
            "Department": st.column_config.TextColumn("Lead Dept", width="small"),
            "Activity Type": st.column_config.TextColumn("Activity", width="medium"),
            "Location": st.column_config.TextColumn("Location", width="medium"),
            "Impact_Count": st.column_config.NumberColumn("Impact Volume", format="%d", help="Beneficiaries, Families, or Educators Deployed"),
            "Status": st.column_config.TextColumn("Status", width="small")
        }
    )

    st.write("---")
    st.write("### 📚 Education Department Operations")
    
    col_edu1, col_edu2, col_edu3, col_edu4 = st.columns(4)
    with col_edu1.container(border=True):
        st.metric("Enrolled Students", f"{len(df_edu_safe)} 🧑‍🎓")
    with col_edu2.container(border=True):
        st.metric("Active Educators", f"{df_edu_log['Educator ID'].nunique()} 🧑‍🏫")
    with col_edu3.container(border=True):
        st.metric("Families Approached", f"{int(df_edu_survey['Families Approached'].sum())} 🏘️")
    with col_edu4.container(border=True):
        st.metric("Teaching Sessions", f"{len(df_edu_log)} 📝")
        
    st.write("#### 🧑‍🎓 Student Profile (Aggregated)")
    st.caption("Only aggregate counts are shown here. Individual records are restricted.")

    if not df_edu_safe.empty and "Age / Grade Level" in df_edu_safe.columns:
        grade_counts = (
            df_edu_safe["Age / Grade Level"].fillna("Unknown").astype(str).str.strip()
            .value_counts().reset_index()
        )
        grade_counts.columns = ["Age / Grade Level", "Students"]
        fig_grade = px.bar(
            grade_counts, x="Age / Grade Level", y="Students",
            template="plotly_dark", color_discrete_sequence=["#3498DB"],
            title="Students by Age / Grade Level"
        )
        st.plotly_chart(fig_grade, width="stretch")
    else:
        st.info("No student data available.")
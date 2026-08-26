import streamlit as st

def render_dept_ops(df_master):
    st.subheader("Departmental Roster Explorer")
    st.write("Department Heads can filter below to isolate and manage their specific team members.")
    
    departments = ["All Departments"] + list(df_master["Department"].unique())
    selected_dept = st.selectbox("Select Department:", departments)
    
    df_filtered = df_master if selected_dept == "All Departments" else df_master[df_master["Department"] == selected_dept]
        
    st.write(f"Showing **{len(df_filtered)}** team members in **{selected_dept}**:")
    
    st.dataframe(
        df_filtered[["Volunteer ID", "Full_Name", "Contact (Email)", "Department", "Total_Events", "Present", "Attendance_Rate", "SOP_Status"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Volunteer ID": st.column_config.TextColumn("ID", width="small"),
            "Full_Name": st.column_config.TextColumn("Volunteer Name", width="medium"),
            "Contact (Email)": st.column_config.TextColumn("Email Address", width="medium"),
            "Total_Events": st.column_config.NumberColumn("Total Events", format="%d 🗓️"),
            "Attendance_Rate": st.column_config.ProgressColumn("Attendance Rate", help="Percentage of events attended", format="%.0f%%", min_value=0, max_value=100),
            "SOP_Status": st.column_config.TextColumn("Standing")
        }
    )
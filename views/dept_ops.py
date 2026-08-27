import streamlit as st
import plotly.express as px

def render_dept_ops(df_master):
    st.subheader("Departmental Roster Explorer")
    st.write("Department Heads can filter below to isolate and manage their specific team members.")
    
    departments = ["All Departments"] + list(df_master["Department"].dropna().unique())
    selected_dept = st.selectbox("Select Department:", departments)
    
    df_filtered = df_master if selected_dept == "All Departments" else df_master[df_master["Department"] == selected_dept]
        
    st.write(f"Showing **{len(df_filtered)}** team members in **{selected_dept}**:")
    
    # NEW: Interactive Engagement Matrix
    if not df_filtered.empty:
        fig_scatter = px.scatter(
            df_filtered, 
            x="Total_Events", 
            y="Attendance_Rate",
            color="SOP_Status", 
            hover_data=["Full_Name", "Volunteer ID"],
            color_discrete_map={"GOOD STANDING": "#2ECC71", "WARNING": "#F1C40F", "STRIKE": "#E74C3C"},
            template="plotly_dark",
            title="Volunteer Engagement (Events vs. Attendance)"
        )
        
        fig_scatter.update_xaxes(dtick=1)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.dataframe(
        df_filtered[["Volunteer ID", "Full_Name", "Contact (Email)", "Department", "Total_Events", "Present", "Attendance_Rate", "SOP_Status"]],
        width="stretch",
        hide_index=True,
        # NEW: Freeze the first two columns on mobile
        column_config={
            "Volunteer ID": st.column_config.TextColumn("ID", width="small"),
            "Full_Name": st.column_config.TextColumn("Volunteer Name", width="medium"),
            "Attendance_Rate": st.column_config.ProgressColumn("Attendance Rate", format="%.0f%%", min_value=0, max_value=100)
        }
    )
import streamlit as st
import plotly.express as px

def render_hr_monitor(df_master):
    st.subheader("Compliance & Certificate Oversight")
    
    # NEW: Foundation-wide HR Health 
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
        st.plotly_chart(fig_hr, use_container_width=True)
    
    col_hr1, col_hr2 = st.columns(2)
    
    with col_hr1:
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
            
    with col_hr2:
        st.write("### 🎓 Certificate Eligible")
        df_eligible = df_master[df_master["SOP_Status"] == "GOOD STANDING"]
        st.dataframe(
            df_eligible[["Volunteer ID", "Full_Name", "Department", "Attendance_Rate"]],
            width="stretch",
            hide_index=True,
            column_config={
                "Attendance_Rate": st.column_config.ProgressColumn("Attendance Rate", format="%.0f%%", min_value=0, max_value=100)
            }
        )
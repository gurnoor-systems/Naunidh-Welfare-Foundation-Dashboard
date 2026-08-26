import streamlit as st

def render_hr_monitor(df_master):
    st.subheader("Compliance & Certificate Oversight")
    
    col_hr1, col_hr2 = st.columns(2)
    
    with col_hr1:
        st.write("### 🚨 High Risk / Warning List (Strikes ≥ 1)")
        df_warnings = df_master[df_master["Total_Strikes"] > 0].sort_values(by="Total_Strikes", ascending=False)
        
        if len(df_warnings) > 0:
            st.dataframe(
                df_warnings[["Volunteer ID", "Full_Name", "Department", "Total_Strikes", "SOP_Status"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Volunteer ID": st.column_config.TextColumn("ID"),
                    "Full_Name": st.column_config.TextColumn("Volunteer Name"),
                    "Total_Strikes": st.column_config.NumberColumn("⚠️ Strike Count", format="%d"),
                    "SOP_Status": st.column_config.TextColumn("Current Standing")
                }
            )
        else:
            st.success("No active strikes logged across the foundation!")
            
    with col_hr2:
        st.write("### 🎓 Certificate Eligible (Good Standing)")
        df_eligible = df_master[df_master["SOP_Status"] == "GOOD STANDING"]
        st.dataframe(
            df_eligible[["Volunteer ID", "Full_Name", "Department", "Attendance_Rate"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Volunteer ID": st.column_config.TextColumn("ID"),
                "Full_Name": st.column_config.TextColumn("Volunteer Name"),
                "Attendance_Rate": st.column_config.ProgressColumn("Attendance Rate", format="%.0f%%", min_value=0, max_value=100)
            }
        )
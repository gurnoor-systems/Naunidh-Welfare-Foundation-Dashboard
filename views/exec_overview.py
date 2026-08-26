import streamlit as st
import plotly.express as px

def render_exec_overview(df_master, df_drives, df_edu_safe, df_edu_survey):
    # ... [Keep your existing metric cards code here] ...

    st.write("### 🏢 Internal Operations Health")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1.container(border=True):
        st.write("#### Roster Breakdown")
        dept_counts = df_master["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        
        fig_bar = px.bar(dept_counts, x="Department", y="Count", 
                         color_discrete_sequence=["#3498DB"], 
                         template="plotly_dark")
        fig_bar.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_bar, use_container_width=True) 

    with col_chart2.container(border=True):
        st.write("#### Standing Status")
        status_counts = df_master["SOP_Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        
        # Create a sleek Donut Chart
        fig_donut = px.pie(status_counts, values="Count", names="Status", hole=0.5,
                           color_discrete_sequence=["#2ECC71", "#E74C3C"],
                           template="plotly_dark")
        fig_donut.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_donut, use_container_width=True)
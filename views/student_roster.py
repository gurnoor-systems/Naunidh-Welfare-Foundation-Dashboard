import streamlit as st


def render_student_roster(df_students):
    st.subheader("Student Roster")
    st.caption(
        "Restricted: visible to the Education division head and Leadership only. "
        "Please do not share screenshots or exports outside these roles."
    )

    if df_students.empty:
        st.info("No student records found.")
        return

    query = st.text_input("Search by student name or ID", "")
    df = df_students
    if query.strip():
        q = query.strip()
        mask = (
            df["Student Name"].astype(str).str.contains(q, case=False, na=False, regex=False)
            | df["Student ID"].astype(str).str.contains(q, case=False, na=False, regex=False)
        )
        df = df[mask]

    st.write(f"Showing **{len(df)}** of **{len(df_students)}** students")
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "Student ID": st.column_config.TextColumn("Student ID", width="small"),
            "Student Name": st.column_config.TextColumn("Student Name", width="medium"),
            "Age / Grade Level": st.column_config.TextColumn("Grade", width="small"),
            "Educator ID(s)": st.column_config.TextColumn("Educator ID(s)", width="medium"),
        },
    )
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

    units = sorted(df_students["Unit"].fillna("Unassigned").astype(str).str.strip().unique())
    c1, c2 = st.columns([2, 1])
    query = c1.text_input("Search by student name or ID", "")
    chosen = c2.multiselect("Unit", units, default=units)
    df = df_students.copy()
    df["Unit"] = df["Unit"].fillna("Unassigned").astype(str).str.strip()
    df = df[df["Unit"].isin(chosen)]

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
            "Unit": st.column_config.TextColumn("Unit", width="small"),
            "Educator ID(s)": st.column_config.TextColumn("Educator ID(s)", width="medium"),
        },
    )
import streamlit as st
from db import run_query, execute_sql

st.set_page_config(page_title="CRUD App", page_icon="🛠️", layout="centered")
st.title("🛠️ CRUD App with Neon Postgres")
st.markdown("### Manage your `users` table easily")

tabs = st.tabs(["➕ Create", "📄 Read", "✏️ Update", "🗑️ Delete"])

# ----------------- CREATE -----------------
with tabs[0]:
    st.subheader("➕ Add New User")
    with st.form("create_user"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        signup_date = st.date_input("Signup Date")
        submit_create = st.form_submit_button("Create User")
        if submit_create:
            try:
                execute_sql(
                    "INSERT INTO users (name, email, signup_date) VALUES (:name, :email, :signup_date)",
                    {"name": name, "email": email, "signup_date": signup_date},
                )
                st.success(f"✅ User '{name}' added successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ----------------- READ -----------------
with tabs[1]:
    st.subheader("📄 View All Users")
    try:
        df = run_query("SELECT * FROM users ORDER BY id DESC")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ----------------- UPDATE -----------------
with tabs[2]:
    st.subheader("✏️ Update User")
    with st.form("update_user"):
        user_id = st.number_input("User ID", min_value=1)
        new_name = st.text_input("New Name")
        new_email = st.text_input("New Email")
        submit_update = st.form_submit_button("Update User")
        if submit_update:
            try:
                execute_sql(
                    "UPDATE users SET name=:name, email=:email WHERE id=:id",
                    {"id": user_id, "name": new_name, "email": new_email},
                )
                st.success(f"✅ User ID {user_id} updated successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ----------------- DELETE -----------------
with tabs[3]:
    st.subheader("🗑️ Delete User")
    with st.form("delete_user"):
        delete_id = st.number_input("User ID to Delete", min_value=1)
        submit_delete = st.form_submit_button("Delete User")
        if submit_delete:
            try:
                execute_sql("DELETE FROM users WHERE id=:id", {"id": delete_id})
                st.success(f"✅ User ID {delete_id} deleted successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")
st.caption("Made by Yaaseen Basit using Streamlit + Neon Postgres")

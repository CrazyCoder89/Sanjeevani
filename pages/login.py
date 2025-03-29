import streamlit as st
import mysql.connector

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# MySQL Database Connection Function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Change to your MySQL host
        user="root",  # Change to your MySQL user
        password="Krish@8904",  # Change to your MySQL password
        database="hms_database"
    )

def check_login(username, password, role):
    """Check login credentials from MySQL database"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=%s AND password=%s AND role=%s", (username, password, role))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None  # Return role (Doctor or Staff)

def show_login():
    """Display login form"""
    st.title("\U0001F511 Login to HMS")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Login as", ["Doctor", "Staff"])  # Added role selection

    if st.button("Login"):
        user_role = check_login(username, password, role)
        if user_role:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user_role
            st.success(f"✅ Welcome, {username}! Role: {user_role}")

            # ✅ Navigate based on role
            if user_role == "Staff":
                st.switch_page("pages/staff_dashboard.py")  
            elif user_role == "Doctor":
                st.switch_page("pages/doctor_dashboard.py")  
        else:
            st.error("❌ Invalid username, password, or role")

if __name__ == "__main__":
    show_login()

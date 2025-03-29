import streamlit as st
import mysql.connector

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# Function to connect to MySQL
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Krish@8904",
            database="hms_database"
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"⚠️ Database Connection Error: {err}")
        return None

# Function to create users table
def create_users_table():
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                username VARCHAR(255) UNIQUE, 
                password VARCHAR(255), 
                role VARCHAR(50)
            )
        ''')
        conn.commit()
        conn.close()

# Check if username exists
def check_username_exists(username):
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = c.fetchone()
        conn.close()
        return user is not None
    return False

# Add new user
def add_user(username, password, role):
    if check_username_exists(username):
        st.error("⚠️ Username already exists. Choose a different one.")
        return

    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                  (username, password, role))
        conn.commit()
        conn.close()
        st.success("✅ Account created successfully! You can now login.")
        st.switch_page("pages/login.py")  # Redirect to login page

# Signup form
def show_signup():
    st.title("📝 Sign Up for HMS")

    create_users_table()  # Ensure the table exists

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.selectbox("Select Role", ["Doctor", "Staff"])

    if st.button("Sign Up"):
        if not username or not password or not confirm_password:
            st.error("⚠️ Please fill in all fields.")
        elif password != confirm_password:
            st.error("⚠️ Passwords do not match!")
        else:
            add_user(username, password, role)

if __name__ == "__main__":
    show_signup()

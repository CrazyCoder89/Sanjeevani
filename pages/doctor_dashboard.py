import streamlit as st
import mysql.connector
from datetime import datetime

# Custom CSS for styling
st.markdown(
    """
    <style>
        .stButton>button {
            width: 100%;
            height: 50px;
            font-size: 18px;
            border-radius: 10px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #4CAF50;
            color: white;
        }
        .header-container {
            text-align: center;
            padding: 10px;
            background-color: #2E3B4E;
            color: white;
            border-radius: 10px;
        }
        .alert-box {
            padding: 10px;
            margin: 10px 0;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
        }
        .alert-danger {
            background-color: #ffcccc;
            border-left: 5px solid #ff0000;
            color: #b30000;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Krish@8904",
        database="hms_database"
    )

# Ensure Emergency Alerts Table Exists
def create_emergency_alerts_table():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emergency_alerts (
                    alert_id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id VARCHAR(50) NOT NULL,
                    bed_number VARCHAR(10) NOT NULL,
                    alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

            # Check if 'resolved' column exists
            cursor.execute("SHOW COLUMNS FROM emergency_alerts LIKE 'resolved'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("ALTER TABLE emergency_alerts ADD COLUMN resolved BOOLEAN DEFAULT FALSE")
                conn.commit()

create_emergency_alerts_table()

# Validate User Session
if "username" not in st.session_state or "role" not in st.session_state:
    st.error("You must be logged in to access the dashboard.")
    st.stop()

doctor_name = st.session_state["username"]
role = st.session_state["role"]

if role != "Doctor":
    st.error("Unauthorized access. This page is for doctors only.")
    st.stop()

# Header
st.markdown(f"<div class='header-container'><h1>\U0001F468‍⚕️ Dr. {doctor_name}'s Dashboard</h1></div>", unsafe_allow_html=True)

st.write("### Choose an option below:")

# Layout with Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("📊 Survival Model Analysis"):
        st.switch_page("pages/survival_analysis.py")
    if st.button("📅 Length of Stay Prediction"):
        st.switch_page("pages/los_prediction.py")
with col2:
    if st.button("📆 Doctor Scheduling"):
        st.switch_page("pages/doctor_schedulling.py")
    if st.button("📋 Patient Medical Records"):
        st.switch_page("pages/patient_records.py")

# Fetch Emergency Alerts
def fetch_emergency_alerts():
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as c:
            c.execute("""
                SELECT ea.alert_id, ea.bed_number, p.name, ea.alert_time 
                FROM emergency_alerts ea
                JOIN patients p ON ea.patient_id = p.patient_id
                WHERE ea.resolved = FALSE
                ORDER BY ea.alert_time DESC
            """)
            return c.fetchall()

# Resolve Emergency Alert
def resolve_alert(alert_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE emergency_alerts SET resolved = TRUE WHERE alert_id = %s", (alert_id,))
            conn.commit()
    st.rerun()

# Emergency Alerts Section
st.markdown("## 🚨 Emergency Alerts")
st.write("⚠ These are urgent alerts from the hospital beds requiring immediate attention.")
alerts = fetch_emergency_alerts()

if alerts:
    for alert in alerts:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(
                f"""
                <div class="alert-box alert-danger">
                    <b>⚠ Emergency Alert</b><br>
                    🛏️ <b>Bed:</b> {alert['bed_number']}<br>
                    🏥 <b>Patient:</b> {alert['name']}<br>
                    ⏰ <b>Time:</b> {alert['alert_time']}
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            if st.button(f"✅ Resolve", key=f"resolve_{alert['alert_id']}"):
                resolve_alert(alert["alert_id"])
else:
    st.info("✅ No emergency alerts at the moment.")

# Refresh Button
st.divider()
if st.button("🔄 Refresh Alerts"):
    st.rerun()

# Footer
st.markdown("---")
st.caption(f"Logged in as: **Dr. {doctor_name}** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Logout Button
if st.button("❌ Logout"):
    st.session_state.clear()
    st.switch_page("Main.py")

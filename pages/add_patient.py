import streamlit as st
import mysql.connector
import uuid  # To generate unique Patient IDs

# Ensure user is logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("pages/login.py")

# Page Configuration
st.set_page_config(page_title="Add New Patient", layout="wide")

st.title("➕ Add New Patient")

# Function to create MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Krish@8904",
        database="hms_database"
    )

# Create Patients Table if Not Exists
conn = get_db_connection()
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id VARCHAR(10) PRIMARY KEY,
        name VARCHAR(255),
        age INT,
        gender ENUM('Male', 'Female'),
        smoking ENUM('No', 'Yes'),
        diabetes ENUM('No', 'Yes'),
        hypertension ENUM('No', 'Yes'),
        CAD ENUM('No', 'Yes'),
        admission_type ENUM('EMERGENCY', 'OPD'),
        HB FLOAT,
        TLC FLOAT,
        glucose FLOAT,
        urea FLOAT,
        creatinine FLOAT,
        BNP FLOAT,
        EF FLOAT
    )
""")
conn.commit()
conn.close()

# Generate a unique Patient ID
patient_id = str(uuid.uuid4())[:8]  # Shorter version of UUID

# Patient Information Form
with st.form("add_patient_form", clear_on_submit=True):
    st.subheader("👤 Patient Information")
    st.text(f"📄 **Generated Patient ID:** {patient_id}")  # Display Patient ID
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.radio("Gender", ("Male", "Female"))

    st.subheader("🏥 Admission Details")
    admission_type = st.selectbox("Admission Type", ("EMERGENCY", "OPD"))  # Fixed label

    st.subheader("🩺 Medical History")
    smoking = st.selectbox("Smoking", ("No", "Yes"))
    diabetes = st.selectbox("Diabetes", ("No", "Yes"))
    hypertension = st.selectbox("Hypertension", ("No", "Yes"))
    CAD = st.selectbox("Coronary Artery Disease (CAD)", ("No", "Yes"))

    st.subheader("🔬 Lab Reports")
    HB = st.number_input("Hemoglobin (HB)", min_value=3.0, max_value=26.5,value=12.6, step=0.1)
    TLC = st.number_input("Total Leukocyte Count (TLC)", min_value=0.1, max_value=50.0,value=8.4, step=0.1)
    glucose = st.number_input("Glucose Level", min_value=40.0, max_value=400.0, value=110.0,step=5.0)
    urea = st.number_input("Urea Level", min_value=0.1, max_value=300.0, value=27.0,step=1.0)
    creatinine = st.number_input("Creatinine Level", min_value=0.06, max_value=15.0, value=0.8,step=0.01)
    BNP = st.number_input("BNP (Brain Natriuretic Peptide)", min_value=4.0, max_value=5000.0, value=500.0,step=10.0)
    EF = st.number_input("Ejection Fraction (EF)", min_value=14.0, max_value=60.0, value=40.0,step=1.0)

    submit_button = st.form_submit_button("✅ Add Patient")

# Insert Data into MySQL Database
if submit_button:
    if name:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO patients (patient_id, name, age, gender, smoking, diabetes, hypertension, CAD, admission_type, HB, TLC, glucose, urea, creatinine, BNP, EF)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, name, age, gender, smoking, diabetes, hypertension, CAD, admission_type, HB, TLC, glucose, urea, creatinine, BNP, EF))
        conn.commit()
        conn.close()
        
        st.success(f"✅ Patient {name} added successfully! 📄 Patient ID: **{patient_id}**")
    else:
        st.error("⚠️ Please enter a valid name!")

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")


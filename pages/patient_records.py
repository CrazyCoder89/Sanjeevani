import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# Function to establish MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",  # Change if hosted elsewhere
        user="root",  # Replace with MySQL username
        password="Krish@8904",  # Replace with MySQL password
        database="hms_database"  # Ensure this database exists
    )

# Initialize Medical Records Table in MySQL
def initialize_medical_records_table():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id VARCHAR(50) NOT NULL,
            visit_date DATE NOT NULL,
            diagnosis TEXT,
            treatment TEXT,
            prescriptions TEXT,
            lab_results TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Call the function to ensure the table exists
initialize_medical_records_table()

# Function to Get Medical Records for a Patient
def get_patient_medical_records(patient_id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT visit_date, diagnosis, treatment, prescriptions, lab_results, notes 
               FROM medical_records WHERE patient_id=%s ORDER BY visit_date DESC"""
    cursor.execute(query, (patient_id,))
    records = cursor.fetchall()
    conn.close()
    
    return pd.DataFrame(records) if records else pd.DataFrame(columns=["visit_date", "diagnosis", "treatment", "prescriptions", "lab_results", "notes"])

# Function to Save a New Medical Record
def save_medical_record(patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    query = """INSERT INTO medical_records (patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes))
    conn.commit()
    cursor.close()
    conn.close()

# Streamlit Page UI
st.title("📋 Patient Medical Records")

# Input for Patient ID
patient_id = st.text_input("🔍 Enter Patient ID to Fetch Records")

# Button to Fetch Records
if st.button("Fetch Medical Records"):
    if patient_id:
        records = get_patient_medical_records(patient_id)
        if not records.empty:
            st.success(f"\u2705 Medical records found for **Patient ID: {patient_id}**")
            st.dataframe(records)
        else:
            st.warning(f"\u26a0\ufe0f No medical records found for **Patient ID: {patient_id}**.")
    else:
        st.error("\u274c Please enter a valid Patient ID.")

# Section to Add New Record
st.header("🆕 Add New Medical Record")

visit_date = st.date_input("📅 Visit Date", datetime.today())
diagnosis = st.text_area("🩺 Diagnosis")
treatment = st.text_area("💊 Treatment Plan")
prescriptions = st.text_area("📝 Prescriptions")
lab_results = st.text_area("🧪 Lab Results")
notes = st.text_area("🗒️ Additional Notes")

if st.button("Save Medical Record"):
    if patient_id and diagnosis:
        save_medical_record(patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes)
        st.success("\u2705 Medical record added successfully!")
    else:
        st.error("\u274c Patient ID and Diagnosis are required to save a record.")

# Back to Dashboard Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/doctor_dashboard.py")

import streamlit as st
import mysql.connector
from datetime import time

# MySQL Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",   
        user="root",        
        password="Krish@8904", 
        database="hms_database"   
    )

# Initialize Tables
def initialize_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS doctor_appointments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        doctor_name VARCHAR(255),
        date DATE,
        start_time TIME,
        end_time TIME,
        mode VARCHAR(50)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS doctor_surgeries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        doctor_name VARCHAR(255),
        date DATE,
        start_time TIME,
        end_time TIME,
        patient_id VARCHAR(100),
        patient_name VARCHAR(255),
        surgery_type VARCHAR(255)
    )
    ''')

    conn.commit()
    conn.close()

initialize_tables()  # Ensure tables exist

st.title("Doctor Dashboard - Manage Appointments & Surgeries")

doctor_name = st.text_input("Enter Your Name (Doctor)")

# Function to Check Time Conflicts
def check_time_conflict(doctor_name, date_selected, start_time, end_time):
    conn = get_connection()
    cur = conn.cursor()

    date_str = date_selected.strftime('%Y-%m-%d')
    start_str = start_time.strftime('%H:%M:%S')
    end_str = end_time.strftime('%H:%M:%S')

    # Check appointments
    cur.execute('''
    SELECT COUNT(*) FROM doctor_appointments
    WHERE doctor_name=%s AND date=%s AND (
        (start_time <= %s AND end_time > %s) OR
        (start_time < %s AND end_time >= %s)
    )
    ''', (doctor_name, date_str, end_str, start_str, start_str, end_str))
    appointment_conflict = cur.fetchone()[0]

    # Check surgeries
    cur.execute('''
    SELECT COUNT(*) FROM doctor_surgeries
    WHERE doctor_name=%s AND date=%s AND (
        (start_time <= %s AND end_time > %s) OR
        (start_time < %s AND end_time >= %s)
    )
    ''', (doctor_name, date_str, end_str, start_str, start_str, end_str))
    surgery_conflict = cur.fetchone()[0]

    conn.close()
    return appointment_conflict > 0 or surgery_conflict > 0

if doctor_name.strip():
    tab1, tab2 = st.tabs(["Manage Appointments", "Schedule Surgery"])

    with tab1:
        st.subheader(f"Appointment Slots for Dr. {doctor_name}")
        date_selected = st.date_input("Appointment Date", key="appointment_date")
        start_time = st.time_input("Appointment Start Time", key="appointment_start_time")
        end_time = st.time_input("Appointment End Time", key="appointment_end_time")
        mode = st.selectbox("Mode", ["in-person", "telemedicine"], key="appointment_mode")

        if st.button("Add Appointment Slot"):
            if check_time_conflict(doctor_name, date_selected, start_time, end_time):
                st.error("Time conflict detected! This slot overlaps with an existing appointment or surgery.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('''
                INSERT INTO doctor_appointments (doctor_name, date, start_time, end_time, mode)
                VALUES (%s, %s, %s, %s, %s)
                ''', (doctor_name, date_selected.strftime('%Y-%m-%d'), 
                      start_time.strftime('%H:%M:%S'), end_time.strftime('%H:%M:%S'), mode))
                conn.commit()
                conn.close()
                st.success("Appointment slot added successfully.")

        st.subheader("Your Appointments")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
        SELECT date, start_time, end_time, mode 
        FROM doctor_appointments 
        WHERE doctor_name=%s ORDER BY date, start_time
        ''', (doctor_name,))
        appointments = cur.fetchall()
        conn.close()

        for row in appointments:
            st.write(f"{row[0]} | {row[1]} - {row[2]} ({row[3]})")

    with tab2:
        st.subheader(f"Surgery Slots for Dr. {doctor_name}")
        surgery_date_selected = st.date_input("Surgery Date", key="surgery_date")
        surgery_start_time = st.time_input("Surgery Start Time", key="surgery_start_time")
        surgery_end_time = st.time_input("Surgery End Time", key="surgery_end_time")
        patient_id = st.text_input("Patient ID", key="surgery_patient_id")
        patient_name = st.text_input("Patient Name", key="surgery_patient_name")
        surgery_type = st.text_input("Surgery Type", key="surgery_type")

        if st.button("Add Surgery Slot"):
            if check_time_conflict(doctor_name, surgery_date_selected, surgery_start_time, surgery_end_time):
                st.error("Time conflict detected! This slot overlaps with an existing appointment or surgery.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('''
                INSERT INTO doctor_surgeries (doctor_name, date, start_time, end_time, patient_id, patient_name, surgery_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (doctor_name, surgery_date_selected.strftime('%Y-%m-%d'), 
                      surgery_start_time.strftime('%H:%M:%S'), surgery_end_time.strftime('%H:%M:%S'),
                      patient_id, patient_name, surgery_type))
                conn.commit()
                conn.close()
                st.success("Surgery slot added successfully.")

        st.subheader("Your Surgeries")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
        SELECT date, start_time, end_time, patient_name, surgery_type
        FROM doctor_surgeries 
        WHERE doctor_name=%s ORDER BY date, start_time
        ''', (doctor_name,))
        surgeries = cur.fetchall()
        conn.close()

        for row in surgeries:
            st.write(f"{row[0]} | {row[1]} - {row[2]} | Patient: {row[3]} | Surgery: {row[4]}")

st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/doctor_dashboard.py")

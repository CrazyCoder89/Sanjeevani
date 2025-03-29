import streamlit as st
import sqlite3
from datetime import datetime

st.title("Staff - Take Patient Appointment")

if "username" not in st.session_state or st.session_state.get("role") != "Staff":
    st.error("Unauthorized access. Please log in as Staff.")
    st.stop()

def get_doctor_slots(doctor_username, date):
    conn = sqlite3.connect("database/hms_database1.db")
    c = conn.cursor()
    c.execute('''SELECT start_time, end_time, consult_type FROM doctor_availability
                 WHERE doctor_username=? AND date=? AND status='Available' ''',
              (doctor_username, date))
    slots = c.fetchall()
    conn.close()
    return slots

def fetch_patient_name(patient_id):
    conn = sqlite3.connect("database/hms_database.db")  # Fetch from patients.db
    c = conn.cursor()
    c.execute('''SELECT name FROM patients WHERE patient_id=?''', (patient_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Inputs
doctor_username = st.text_input("Enter Doctor Username")
date = st.date_input("Appointment Date", min_value=datetime.today())

if doctor_username and date:
    slots = get_doctor_slots(doctor_username, date)
    if slots:
        slot_display = [f"{start}-{end} ({consult_type})" for start, end, consult_type in slots]
        chosen_slot = st.selectbox("Choose an Available Slot", slot_display)
        start_time, end_time, consult_type = slots[slot_display.index(chosen_slot)]

        patient_id = st.text_input("Enter Patient ID")
        if patient_id:
            patient_name = fetch_patient_name(patient_id)
            if patient_name:
                st.write(f"**Patient Name:** {patient_name}")

                if st.button("Confirm Appointment"):
                    conn = sqlite3.connect("database/hms_database1.db")
                    c = conn.cursor()

                    # Check for duplicate appointment
                    c.execute('''SELECT 1 FROM appointments WHERE doctor_username=? AND date=? AND start_time=?''',
                              (doctor_username, date, start_time))
                    if c.fetchone():
                        st.error("This slot is already booked.")
                    else:
                        c.execute('''INSERT INTO appointments (doctor_username, patient_id, patient_name, date, start_time, end_time, consult_type, status)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, 'Booked')''',
                                  (doctor_username, patient_id, patient_name, date, start_time, end_time, consult_type))

                        # Update doctor's availability status
                        c.execute('''UPDATE doctor_availability
                                     SET status='Booked'
                                     WHERE doctor_username=? AND date=? AND start_time=? AND end_time=?''',
                                  (doctor_username, date, start_time, end_time))

                        conn.commit()
                        conn.close()
                        st.success("Appointment Booked Successfully!")
            else:
                st.error("Patient ID not found in system.")
    else:
        st.warning("No available slots found for this doctor on the selected date.")

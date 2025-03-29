import streamlit as st
import mysql.connector
import pandas as pd

# Connect to MySQL Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Krish@8904",
    database="hms_database"
)
cur = conn.cursor()

# Ensure tables exist at startup
cur.execute('''
CREATE TABLE IF NOT EXISTS booked_appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT,
    doctor_name VARCHAR(255),
    date DATE,
    start_time TIME,
    end_time TIME,
    mode VARCHAR(50),
    patient_id VARCHAR(255),
    patient_name VARCHAR(255)
)
''')
conn.commit()

st.title("Staff Dashboard - Manage Appointments & Surgeries")

doctor_name = st.text_input("Enter Doctor's Name to Manage")

if doctor_name.strip():
    tab1, tab2 = st.tabs(["Manage Appointments", "View Surgeries"])

    with tab1:
        st.subheader(f"Available Appointment Slots for Dr. {doctor_name}")

        cur.execute('''
        SELECT id, date, start_time, end_time, mode 
        FROM doctor_appointments 
        WHERE doctor_name=%s ORDER BY date, start_time
        ''', (doctor_name,))
        appointments = cur.fetchall()

        if not appointments:
            st.info("No available slots.")
        else:
            df = pd.DataFrame(appointments, columns=["ID", "Date", "Start Time", "End Time", "Mode"])
            st.dataframe(df)

            selected_id = st.selectbox("Select Slot ID to Book", df['ID'])
            patient_id = st.text_input("Patient ID")
            patient_name = st.text_input("Patient Name")

            if st.button("Book Appointment"):
                cur.execute('''
                SELECT COUNT(*) FROM booked_appointments WHERE appointment_id=%s
                ''', (selected_id,))
                if cur.fetchone()[0] > 0:
                    st.error("This slot is already booked.")
                elif not patient_id or not patient_name:
                    st.error("Please enter both Patient ID and Name.")
                else:
                    cur.execute('''
                    SELECT date, start_time, end_time, mode FROM doctor_appointments WHERE id=%s
                    ''', (selected_id,))
                    date, start_time, end_time, mode = cur.fetchone()

                    cur.execute('''
                    INSERT INTO booked_appointments (appointment_id, doctor_name, date, start_time, end_time, mode, patient_id, patient_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (selected_id, doctor_name, date, start_time, end_time, mode, patient_id, patient_name))

                    cur.execute('DELETE FROM doctor_appointments WHERE id=%s', (selected_id,))
                    conn.commit()
                    st.success(f"Appointment booked for {patient_name}.")

        st.subheader(f"Booked Appointments for Dr. {doctor_name}")
        cur.execute('''
        SELECT id, date, start_time, end_time, mode, patient_id, patient_name 
        FROM booked_appointments 
        WHERE doctor_name=%s ORDER BY date, start_time
        ''', (doctor_name,))
        booked = cur.fetchall()

        if not booked:
            st.info("No appointments booked.")
        else:
            df_booked = pd.DataFrame(booked, columns=["ID", "Date", "Start Time", "End Time", "Mode", "Patient ID", "Patient Name"])
            st.dataframe(df_booked)

            cancel_id = st.selectbox("Select Booking ID to Cancel", df_booked['ID'])

            if st.button("Cancel Appointment"):
                cur.execute('DELETE FROM booked_appointments WHERE id=%s', (cancel_id,))
                conn.commit()
                st.success("Appointment cancelled successfully.")
                st.rerun()

    with tab2:
        st.subheader(f"Scheduled Surgeries for Dr. {doctor_name}")

        cur.execute('''
        CREATE TABLE IF NOT EXISTS doctor_surgeries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            doctor_name VARCHAR(255),
            date DATE,
            start_time TIME,
            end_time TIME,
            patient_id VARCHAR(255),
            patient_name VARCHAR(255),
            surgery_type VARCHAR(255)
        )
        ''')
        conn.commit()

        cur.execute('''
        SELECT date, start_time, end_time, patient_id, patient_name, surgery_type 
        FROM doctor_surgeries 
        WHERE doctor_name=%s ORDER BY date, start_time
        ''', (doctor_name,))
        surgeries = cur.fetchall()

        if not surgeries:
            st.info("No surgeries scheduled.")
        else:
            df_surgeries = pd.DataFrame(surgeries, columns=["Date", "Start Time", "End Time", "Patient ID", "Patient Name", "Surgery Type"])
            st.dataframe(df_surgeries)

conn.close()
# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")

import streamlit as st
import mysql.connector
from datetime import datetime

# MySQL Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Krish@8904",
        database="hms_database"
    )

# Initialize MySQL Tables
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create tables if not exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS hospital_beds (
            ward_type VARCHAR(50) PRIMARY KEY,
            total_beds INT NOT NULL,
            occupied_beds INT NOT NULL,
            available_beds INT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS patient_beds (
            patient_id VARCHAR(50) PRIMARY KEY,
            ward_type VARCHAR(50),
            bed_assigned INT UNIQUE,
            assigned_at TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100),
            age INT,
            gender VARCHAR(10)
        )
    """)

    # Ensure Emergency Alerts Table Exists
    c.execute("""
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
    conn.close()

init_db()

# Fetch Current Bed Status
def fetch_bed_status():
    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM hospital_beds")
    data = c.fetchall()
    conn.close()
    return data

# Get all admitted patients
def fetch_all_admitted_patients():
    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    c.execute("""
        SELECT pb.patient_id, p.name, pb.ward_type, pb.bed_assigned, pb.assigned_at 
        FROM patient_beds pb
        JOIN patients p ON pb.patient_id = p.patient_id
        ORDER BY pb.ward_type, pb.bed_assigned
    """)
    data = c.fetchall()
    conn.close()
    return data

# Check if patient exists
def check_patient_exists(patient_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    patient = c.fetchone()
    conn.close()
    return patient is not None

# Check if bed is available
def is_bed_available(bed_number):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patient_beds WHERE bed_assigned = %s", (bed_number,))
    occupied = c.fetchone()
    conn.close()
    return occupied is None

# Assign a Bed to a Patient
def assign_bed(patient_id, ward_type, bed_number):
    if not check_patient_exists(patient_id):
        return False, "❌ Patient not found in the database!"
    
    if not is_bed_available(bed_number):
        return False, f"❌ Bed {bed_number} is already occupied!"
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Insert the assigned bed
    c.execute("""
        INSERT INTO patient_beds (patient_id, ward_type, bed_assigned, assigned_at) 
        VALUES (%s, %s, %s, %s)
    """, (patient_id, ward_type, bed_number, datetime.now()))

    # Update bed count
    c.execute("""
        UPDATE hospital_beds 
        SET occupied_beds = occupied_beds + 1, available_beds = available_beds - 1 
        WHERE ward_type = %s
    """, (ward_type,))

    conn.commit()
    conn.close()
    return True, f"✅ Bed {bed_number} assigned to patient {patient_id} in {ward_type}."

# Revoke a Bed Assignment
def revoke_bed(patient_id):
    if not check_patient_exists(patient_id):
        return False, "❌ Patient not found in the database!"
    
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT ward_type, bed_assigned FROM patient_beds WHERE patient_id = %s", (patient_id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return False, "❌ No bed found for this patient."

    ward_type, bed_number = result
    c.execute("DELETE FROM patient_beds WHERE patient_id = %s", (patient_id,))
    c.execute("""
        UPDATE hospital_beds 
        SET occupied_beds = occupied_beds - 1, available_beds = available_beds + 1 
        WHERE ward_type = %s
    """, (ward_type,))

    conn.commit()
    conn.close()
    return True, f"✅ Bed {bed_number} revoked for patient {patient_id}."

# Streamlit UI
st.title("🏥 Hospital Bed Management")

# Display Bed Availability Table
st.write("### Current Bed Status")
hospital_data = fetch_bed_status()

if hospital_data:
    st.dataframe(hospital_data)
else:
    st.write("🚨 No data available!")

# Display all admitted patients
st.write("### Admitted Patients in ICU & Ward")
admitted_patients = fetch_all_admitted_patients()

if admitted_patients:
    st.dataframe(admitted_patients)
else:
    st.write("🚨 No admitted patients found!")

# Assign Bed Section
st.write("### Assign Bed")
patient_id = st.text_input("Enter Patient ID:")
ward_type = st.selectbox("Select Ward Type:", ["ICU", "Ward"])
bed_number = st.number_input("Enter Bed Number:", min_value=100, max_value=249, step=1)

if st.button("🛏️ Assign Bed"):
    if not patient_id.strip():
        st.warning("⚠ Please enter a valid Patient ID.")
    else:
        success, message = assign_bed(patient_id.strip(), ward_type, bed_number)
        if success:
            st.success(message)
        else:
            st.error(message)
        st.rerun()


# Revoke Bed Section
st.write("### Revoke Bed")
revoke_patient_id = st.text_input("Enter Patient ID to Revoke Bed:")

if st.button("❌ Revoke Bed"):
    if not revoke_patient_id.strip():
        st.warning("⚠ Please enter a valid Patient ID.")
    else:
        success, message = revoke_bed(revoke_patient_id.strip())
        if success:
            st.success(message)
        else:
            st.error(message)
        st.rerun()

# SOS Emergency Alert - FIXED ✅
st.write("### 🚨 SOS Emergency Alert")
selected_bed = st.text_input("Enter Bed Number for Emergency Alert:")

if st.button("⚠️ Trigger SOS Alert"):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if the bed is assigned to a patient
    c.execute("SELECT patient_id FROM patient_beds WHERE bed_assigned = %s", (selected_bed,))
    occupied = c.fetchone()
    
    if occupied:
        patient_id = occupied[0]
        
        # Insert into emergency_alerts table
        c.execute("""
            INSERT INTO emergency_alerts (patient_id, bed_number, alert_time, resolved)
            VALUES (%s, %s, NOW(), FALSE)
        """, (patient_id, selected_bed))
        
        conn.commit()
        conn.close()
        
        st.success(f"🚨 Emergency Alert Sent! Doctor Notified for Bed {selected_bed}.")
    else:
        conn.close()
        st.warning("⚠ This bed is not occupied.")

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")

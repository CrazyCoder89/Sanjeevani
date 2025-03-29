import mysql.connector
import pickle
import numpy as np
import pandas as pd
import streamlit as st

# -------- Initialize Session State --------
if "page" not in st.session_state:
    st.session_state["page"] = "pharmacy"
if "pharmacy_total" not in st.session_state:
    st.session_state["pharmacy_total"] = 0
if "disease_total" not in st.session_state:
    st.session_state["disease_total"] = 0
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = ""
if "selected_diseases" not in st.session_state:
    st.session_state["selected_diseases"] = []

# -------- Disease Price Mapping --------
disease_prices = {
    "STABLE ANGINA": 7000, "ACS": 12000, "STEMI": 15000, "ATYPICAL CHEST PAIN": 6000,
    "HEART FAILURE": 18000, "HFREF": 16000, "HFNEF": 14000, "VALVULAR": 10000,
    "CHB": 11000, "SSS": 10500, "AKI": 12500, "CVA INFRACT": 13500, "CVA BLEED": 14000,
    "AF": 9000, "VT": 13000, "PSVT": 9500, "CONGENITAL": 20000, "UTI": 5000,
    "NEURO CARDIOGENIC SYNCOPE": 8000, "ORTHOSTATIC": 7000, "INFECTIVE ENDOCARDITIS": 17000,
    "DVT": 11000, "CARDIOGENIC SHOCK": 25000, "SHOCK": 20000, "PULMONARY EMBOLISM": 22000,
    "CHEST INFECTION": 7500
}

# -------- Database Setup --------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Krish@8904",
        database="hms_database"
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure billing table exists with required columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            patient_id VARCHAR(255) PRIMARY KEY,
            pharmacy_total FLOAT DEFAULT 0,
            hospital_total FLOAT DEFAULT 0,
            disease_total FLOAT DEFAULT 0,
            diseases TEXT,
            grand_total FLOAT DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def fetch_patient_details(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT age, gender, admission_type FROM patients WHERE patient_id = %s", (patient_id,))
    patient_details = cursor.fetchone()
    conn.close()
    return patient_details if patient_details else (None, None, None)

init_db()

def update_bill(patient_id, pharmacy_total, hospital_total, disease_total, diseases, grand_total):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM billing WHERE patient_id = %s", (patient_id,))
    existing_record = cursor.fetchone()
    
    diseases_str = ", ".join(diseases)  # Store diseases as a comma-separated string
    
    if existing_record:
        cursor.execute("""
            UPDATE billing
            SET pharmacy_total = %s, hospital_total = %s, disease_total = %s, diseases = %s, grand_total = %s
            WHERE patient_id = %s
        """, (pharmacy_total, hospital_total, disease_total, diseases_str, grand_total, patient_id))
    else:
        cursor.execute("""
            INSERT INTO billing (patient_id, pharmacy_total, hospital_total, disease_total, diseases, grand_total)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (patient_id, pharmacy_total, hospital_total, disease_total, diseases_str, grand_total))
    
    conn.commit()
    conn.close()

# -------- PHARMACY BILL PAGE --------
def pharmacy_bill():
    st.title("🛒 Pharmacy Billing System")
    
    patient_id = st.text_input("Enter Patient ID:", value=st.session_state["patient_id"])
    st.session_state["patient_id"] = patient_id.strip()
    
    if not patient_id:
        st.warning("⚠ Please enter a valid Patient ID to proceed.")
        return
    
    medicines = st.number_input("💊 Medicines Cost (₹)", min_value=0, value=500)
    injections = st.number_input("💉 Injections Cost (₹)", min_value=0, value=300)
    surgical_items = st.number_input("🔪 Surgical Items Cost (₹)", min_value=0, value=1000)
    consultation_fee = st.number_input("🩺 Consultation Fee (₹)", min_value=0, value=700)
    lab_tests = st.number_input("🔬 Lab Tests Cost (₹)", min_value=0, value=1500)
    
    pharmacy_total = medicines + injections + surgical_items + consultation_fee + lab_tests
    
    # Disease selection
    selected_diseases = st.multiselect("🦠 Select Diagnosed Diseases", list(disease_prices.keys()), default=st.session_state["selected_diseases"])
    st.session_state["selected_diseases"] = selected_diseases
    
    # Calculate total disease cost
    disease_total = sum(disease_prices[disease] for disease in selected_diseases)
    st.session_state["disease_total"] = disease_total
    
    if st.button("Proceed to Hospital Bill"):
        st.session_state["pharmacy_total"] = pharmacy_total
        st.session_state["page"] = "hospital"
        st.rerun()

# -------- HOSPITAL BILL PAGE --------
def hospital_bill():
    st.title("🏥 Hospital Bill Estimator")
    
    patient_id = st.session_state["patient_id"]
    st.subheader(f"Patient ID: {patient_id}")
    
    age, gender, admission_type = fetch_patient_details(patient_id)
    if age is None:
        st.error("Patient details not found! Please enter a valid Patient ID.")
        return
    
    st.write(f"👤 Age: {age}")
    st.write(f"⚧ Gender: {gender}")
    st.write(f"🏥 Admission Type: {admission_type}")
    
    with open("models/hospital_bill.pkl", "rb") as file:
        model = pickle.load(file)
    with open("models/feature_names.pkl", "rb") as f:
        feature_names = pickle.load(f)
    
    los = st.number_input("⏳ Length of Stay (Days)", min_value=1, max_value=30, value=5)
    
    gender_encoded = 0 if gender == "Male" else 1
    admission_encoded = 0 if admission_type == "General Ward" else 1
    
    input_dict = {"Age": age, "Gender_Female": gender_encoded, "Admission_Type_ICU": admission_encoded, "Length_of_Stay": los}
    input_df = pd.DataFrame([input_dict]).reindex(columns=feature_names, fill_value=0)
    
    if st.button("Estimate Total Bill"):
        base_bill = model.predict(input_df)[0]
        stay_charge = los * 1500  # ₹1500 per day stay charge
        admission_charge = 5000 if admission_type == "ICU" else 2000  # ICU ₹5000, Ward ₹2000
        hospital_total = base_bill + stay_charge + admission_charge
        grand_total = hospital_total + st.session_state["pharmacy_total"] + st.session_state["disease_total"]
    
        update_bill(patient_id, st.session_state["pharmacy_total"], hospital_total, 
                    st.session_state["disease_total"], st.session_state["selected_diseases"], grand_total)
    
        # **Display Final Bill Breakdown**
        st.subheader("📌 Detailed Bill Breakdown")
        st.write(f"🦠 **Diagnosed Diseases:** {', '.join(st.session_state['selected_diseases']) if st.session_state['selected_diseases'] else 'None'}")
        st.write(f"💊 **Total Pharmacy Bill:** ₹{st.session_state['pharmacy_total']:,.2f}")
        st.write(f"🏥 **Total Disease Treatment Cost:** ₹{st.session_state['disease_total']:,.2f}")
        st.write(f"🛏 **Hospital Stay Charge:** ₹{stay_charge:,.2f}")
        st.write(f"🛏 **Admission Charge:** ₹{admission_charge:,.2f}")
        st.write(f"💰 **Total Hospital Bill (Excluding Pharmacy & Disease Costs):** ₹{hospital_total:,.2f}")
        
        st.success(f"💵 **Grand Total (Final Bill Amount): ₹{grand_total:,.2f}**")

if st.session_state["page"] == "pharmacy":
    pharmacy_bill()
else:
    hospital_bill()
    
# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")

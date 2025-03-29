import streamlit as st
import mysql.connector
import pickle
import numpy as np

# Load ICU and Ward LOS models
@st.cache_resource
def load_model(file_path):
    with open(file_path, "rb") as file:
        return pickle.load(file)

icu_model = load_model(r"C:\Users\KRISH\.spyder-py3\HMS\models\random_forest_icu.pkl")  # ICU Model
ward_model = load_model(r"C:\Users\KRISH\.spyder-py3\HMS\models\xgboost_ward.pkl")  # Ward Model

# MySQL Database Connection
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",  
        user="root",  
        password="Krish@8904",  
        database="hms_database"  
    )

# Fetch patient data from MySQL
def get_patient_data(patient_id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row
    return None

# Update patient data in MySQL
def save_patient_data(patient_id, additional_data):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """UPDATE patients SET platelets=%s, acs=%s, hfref=%s, stemi=%s, chb=%s, af=%s, vt=%s, uti=%s, 
        cardiogenic_shock=%s, shock=%s, pulmonary_embolism=%s, rural=%s WHERE patient_id=%s""",
        (
            additional_data["platelets"], additional_data["acs"], additional_data["hfref"], 
            additional_data["stemi"], additional_data["chb"], additional_data["af"], 
            additional_data["vt"], additional_data["uti"], additional_data["cardiogenic_shock"], 
            additional_data["shock"], additional_data["pulmonary_embolism"], additional_data["rural"],
            patient_id
        )
    )
    conn.commit()
    conn.close()

# Select ICU or Ward
st.title("🏥 Length of Stay (LOS) Prediction")

ward_type = st.selectbox("🏥 Select Patient Type:", ["ICU", "Ward"])
selected_model = icu_model if ward_type == "ICU" else ward_model

# Patient ID Input
patient_id = st.text_input("🔍 Enter Patient ID to Fetch Details")
patient_data = None

# Fetch Details Button
if st.button("Fetch Details"):
    patient_data = get_patient_data(patient_id)
    if patient_data:
        st.success(f"✅ Data Found for **{patient_data['name']}**")
    else:
        st.error("❌ Patient Not Found! Please enter details manually.")

# Take inputs (Either from database or manually)
st.header("📌 Enter Patient Details")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=0, max_value=120, value=patient_data["age"] if patient_data else 50)
    hb = st.number_input("HB", min_value=3.0, max_value=26.5, value=patient_data["HB"] if patient_data else 12.6)
    tlc = st.number_input("TLC", min_value=0.1, max_value=500.0, value=patient_data["TLC"] if patient_data else 8.4)

with col2:
    glucose = st.number_input("Glucose", min_value=40.0, max_value=400.0, value=patient_data["glucose"] if patient_data else 110.0)
    urea = st.number_input("Urea", min_value=1.0, max_value=300.0, value=patient_data["urea"] if patient_data else 27.0)
    creatinine = st.number_input("Creatinine", min_value=0.06, max_value=15.0, value=patient_data["creatinine"] if patient_data else 0.8)

with col3:
    ef = st.number_input("EF", min_value=14.0, max_value=60.0, value=patient_data["EF"] if patient_data else 40.0)
    bnp = st.number_input("BNP", min_value=4.0, max_value=5000.0, value=patient_data["BNP"] if patient_data else 500.0)
    admission_type = st.radio("Type of Admission", ["Emergency", "OPD"], index=0 if patient_data and patient_data["admission_type"] == 1 else 1)

admission_type = 1 if admission_type == "Emergency" else 0
cad = st.radio("Coronary Artery Disease (CAD)?", ["Yes", "No"], index=0 if patient_data and patient_data["CAD"] == 1 else 1)
cad = 1 if cad == "Yes" else 0

# Additional Details
st.header("📌 Additional Patient Details")

col4, col5, col6 = st.columns(3)

with col4:
    platelets = st.number_input("Platelets", min_value=0.0, max_value=1000.0, value=100.0)
    rural = st.radio("Rural?", ["Yes", "No"])
    acs = st.radio("Acute Coronary Syndrome (ACS)?", ["Yes", "No"])
    cardiogenic_shock = st.radio("Cardiogenic Shock?", ["Yes", "No"])


with col5:
    hfref = st.radio("Heart Failure (HFREF)?", ["Yes", "No"])
    stemi = st.radio("STEMI?", ["Yes", "No"])
    chb = st.radio("Complete Heart Block (CHB)", ["Yes", "No"])
    shock = st.radio("Shock?", ["Yes", "No"])


with col6:
    af = st.radio("Atrial Fibrillation (AF)?", ["Yes", "No"])
    vt = st.radio("Ventricular Tachycardia (VT)?", ["Yes", "No"])
    uti = st.radio("Urinary Tract Infection (UTI)?", ["Yes", "No"])
    pulmonary_embolism = st.radio("Pulmonary Embolism?", ["Yes", "No"])

# Convert categorical inputs to numerical
rural = 1 if rural == "Yes" else 0
acs = 1 if acs == "Yes" else 0
hfref = 1 if hfref == "Yes" else 0
stemi = 1 if stemi == "Yes" else 0
chb = 1 if chb == "Yes" else 0
af = 1 if af == "Yes" else 0
vt = 1 if vt == "Yes" else 0
uti = 1 if uti == "Yes" else 0
cardiogenic_shock = 1 if cardiogenic_shock == "Yes" else 0
shock = 1 if shock == "Yes" else 0
pulmonary_embolism = 1 if pulmonary_embolism == "Yes" else 0

# Convert input to NumPy array
input_features = np.array([
    hb, tlc, platelets, glucose, urea, creatinine, ef, bnp,
    age, rural, admission_type, cad, acs, hfref, stemi, chb, af, vt, uti, 
    cardiogenic_shock, shock, pulmonary_embolism
]).reshape(1, -1)

# Predict button
if st.button("Predict LOS"):
    prediction = selected_model.predict(input_features)[0]
    st.success(f"🛏️ Predicted Length of Stay: {prediction:.2f} days")

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/doctor_dashboard.py")

import streamlit as st
import pandas as pd
import sqlite3
import pickle
import numpy as np

# Load model correctly
with open('models/multi_target_model.pkl', 'rb') as file:
    model_data = pickle.load(file)

fitted_model = model_data['fitted_model']
scaler = model_data['scaler']
feature_cols = model_data['features']
disease_labels = model_data['targets']

# Streamlit App
st.title("🩺 Patient Risk Analysis")

patient_id = st.text_input("Enter Patient ID:")

if patient_id:
    conn = sqlite3.connect('HMS.db')
    query = """
    SELECT age, gender, smoking, diabetes, hypertension, CAD,
           admission_type, HB, TLC, glucose, urea, creatinine, BNP, EF
    FROM patients WHERE patient_id = ?
    """
    patient_data = pd.read_sql_query(query, conn, params=(patient_id,))
    conn.close()

    if patient_data.empty:
        st.error(f"No patient found with ID {patient_id}")
    else:
        # Take additional inputs directly from user (since DB does not have them)
        rural = st.selectbox("Rural (1=Yes, 0=No)", [0, 1])
        alcohol = st.selectbox("Alcohol (1=Yes, 0=No)", [0, 1])
        prior_cmp = st.selectbox("Prior CMP (1=Yes, 0=No)", [0, 1])
        ckd = st.selectbox("Chronic Kidney Disease (1=Yes, 0=No)", [0, 1])
        platelets = st.number_input("Platelets Count", min_value=0.0)

        # Add these to patient data
        patient_data['RURAL'] = rural
        patient_data['ALCOHOL'] = alcohol
        patient_data['PRIOR CMP'] = prior_cmp
        patient_data['CKD'] = ckd
        patient_data['PLATELETS'] = platelets

        # Rename for consistency with trained model
        patient_data.columns = patient_data.columns.str.upper()
        patient_data.rename(columns={'ADMISSION_TYPE': 'TYPE OF ADMISSION-EMERGENCY/OPD'}, inplace=True)

        # Reorder columns to match training
        patient_data = patient_data[feature_cols]

        # Scale and predict
        patient_scaled = scaler.transform(patient_data)
        prediction = fitted_model.predict(patient_scaled)[0]

        # Show result
        result_df = pd.DataFrame({
            "Condition": disease_labels,
            "Risk (1=Present, 0=Absent)": prediction
        })

        st.write(result_df.style.applymap(lambda x: 'background-color: lightcoral' if x == 1 else 'background-color: lightgreen'))


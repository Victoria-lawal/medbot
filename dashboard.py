# dashboard.py
import streamlit as st
import json
import pandas as pd
import os

RECORDS_PATH = "patient_id/data/patient_records.json"

st.set_page_config(page_title="MedBot Patient Dashboard", layout="wide")
st.title("MedBot Patient Records")

def load_records():
    if os.path.exists(RECORDS_PATH):
        with open(RECORDS_PATH, "r") as f:
            return json.load(f)
    return {}

def save_records(records):
    with open(RECORDS_PATH, "w") as f:
        json.dump(records, f, indent=2)

records = load_records()

if not records:
    st.info("No patients recorded yet.")
else:
    patient_names = list(records.keys())
    selected = st.selectbox("Select patient", patient_names)

    if selected:
        data = records[selected]

        st.subheader("Medication Assignment")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            new_compartment = st.number_input(
                "Compartment", min_value=1, max_value=20,
                value=data.get("compartment") or 1
            )
        with col2:
            new_medication = st.text_input(
                "Medication", value=data.get("medication") or ""
            )
        with col3:
            st.write("")
            st.write("")
            if st.button("Save"):
                records[selected]["compartment"] = new_compartment
                records[selected]["medication"] = new_medication
                save_records(records)
                st.success("Saved!")
                st.rerun()

        st.subheader("Vitals History")
        if data["history"]:
            df = pd.DataFrame(data["history"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.dataframe(df, use_container_width=True)

            chart_df = df.dropna(subset=["temp", "bpm", "spo2"], how="all").set_index("timestamp")
            if not chart_df.empty:
                st.line_chart(chart_df[["temp", "bpm", "spo2"]])
        else:
            st.info("No readings recorded yet.")

    st.divider()
    if st.button("Delete selected patient"):
        del records[selected]
        save_records(records)
        st.success(f"Deleted {selected}")
        st.rerun()

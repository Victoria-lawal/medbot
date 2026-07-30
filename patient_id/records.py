import json
import os
from datetime import datetime

RECORDS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'patient_records.json')

def load_records():
    if os.path.exists(RECORDS_PATH):
        with open(RECORDS_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_records(records):
    os.makedirs(os.path.dirname(RECORDS_PATH), exist_ok=True)
    with open(RECORDS_PATH, 'w') as f:
        json.dump(records, f, indent=2)

def log_reading(name, temp, bpm, spo2):
    records = load_records()
    if name not in records:
        records[name] = {"compartment": None, "medication": None, "history": []}
    records[name]["history"].append({
        "timestamp": datetime.now().isoformat(),
        "temp": temp,
        "bpm": bpm,
        "spo2": spo2
    })
    save_records(records)

def set_medication(name, compartment, medication):
    records = load_records()
    if name not in records:
        records[name] = {"compartment": None, "medication": None, "history": []}
    records[name]["compartment"] = compartment
    records[name]["medication"] = medication
    save_records(records)

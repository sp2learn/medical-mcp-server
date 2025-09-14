"""
Patient Data Manager - Manages patient data from doctor_data and whoop_data folders
"""

import pandas as pd
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class PatientDataManager:
    def __init__(self):
        self.patients = {}
        self.visits = []
        self.whoop_data = {}
        self._load_patient_data()
    
    def _load_patient_data(self):
        """Load patient data from doctor_data and whoop_data folders."""
        try:
            # Load patients from doctor_data
            if os.path.exists("doctor_data/patients.csv"):
                patients_df = pd.read_csv("doctor_data/patients.csv")
                for _, patient in patients_df.iterrows():
                    patient_id = f"{patient['first_name'].lower()}_{patient['last_name'].lower()}"
                    
                    # Handle conditions
                    conditions_str = patient.get('conditions', '')
                    if pd.isna(conditions_str) or conditions_str == 'n/a':
                        conditions = []
                    else:
                        conditions = [c.strip() for c in str(conditions_str).split(',') if c.strip()]
                    
                    # Handle medications
                    medications_str = patient.get('medications', '')
                    if pd.isna(medications_str) or medications_str == 'n/a':
                        medications = []
                    else:
                        medications = [m.strip() for m in str(medications_str).split(',') if m.strip()]
                    
                    self.patients[patient_id] = {
                        "id": patient_id,
                        "patient_id": patient['patient_id'],
                        "name": f"{patient['first_name']} {patient['last_name']}",
                        "first_name": patient['first_name'],
                        "last_name": patient['last_name'],
                        "age": patient['age'],
                        "gender": patient['gender'],
                        "height_cm": patient.get('height_cm'),
                        "weight_kg": patient.get('weight_kg'),
                        "blood_type": patient.get('blood_type'),
                        "conditions": conditions,
                        "medications": medications,
                        "last_visit": patient.get('last_visit'),
                        "email": patient.get('email')
                    }
            
            # Load visits from doctor_data
            if os.path.exists("doctor_data/visits.json"):
                with open("doctor_data/visits.json", 'r') as f:
                    self.visits = json.load(f)
            
            # Load Whoop data (only for Amos)
            self._load_whoop_data()
            
        except Exception as e:
            print(f"Error loading patient data: {e}")
    
    def _load_whoop_data(self):
        """Load Whoop data for Amos only."""
        whoop_files = {
            'sleep': 'whoop_data/sleeps.csv',
            'workouts': 'whoop_data/workouts.csv',
            'cycles': 'whoop_data/physiological_cycles.csv',
            'journal': 'whoop_data/journal_entries.csv'
        }
        
        for data_type, file_path in whoop_files.items():
            if os.path.exists(file_path):
                self.whoop_data[data_type] = pd.read_csv(file_path)
    
    def has_whoop_data(self, patient_name: str) -> bool:
        """Check if patient has Whoop data (only Amos does)."""
        return patient_name.lower() in ['amos', 'amos_appendino'] or 'amos' in patient_name.lower()
    
    def get_whoop_not_connected_message(self, patient_name: str) -> str:
        """Return message for patients without Whoop data."""
        return f"{patient_name} has not connected their Whoop account. Only Amos Appendino has Whoop data available."
    
    def find_patient(self, query: str) -> Optional[Dict]:
        """Find patient by name or ID."""
        query = query.lower().strip()
        
        # Direct ID match
        if query in self.patients:
            return self.patients[query]
        
        # Name search
        for patient_id, patient in self.patients.items():
            if query in patient["name"].lower():
                return patient
        
        return None
    
    def find_patient_by_identifier(self, patient_identifier: Dict) -> Optional[Dict]:
        """Find patient by identifier (first_name, last_name, or patient_id)."""
        if "patient_id" in patient_identifier:
            # Search by patient_id
            for patient in self.patients.values():
                if patient["patient_id"] == patient_identifier["patient_id"]:
                    return patient
        
        if "first_name" in patient_identifier and "last_name" in patient_identifier:
            # Search by name
            first_name = patient_identifier["first_name"].lower()
            last_name = patient_identifier["last_name"].lower()
            patient_key = f"{first_name}_{last_name}"
            return self.patients.get(patient_key)
        
        return None
    
    def get_patient_visits(self, patient_identifier: Dict) -> Dict:
        """Get patient's visit history."""
        patient = self.find_patient_by_identifier(patient_identifier)
        if not patient:
            return {"error": "Patient not found"}
        
        # Filter visits for this patient
        patient_visits = [
            visit for visit in self.visits 
            if visit.get("patient_id") == patient["patient_id"]
        ]
        
        return {
            "patient_name": patient["name"],
            "total_visits": len(patient_visits),
            "visits": patient_visits
        }
    
    def get_patient_overview(self, patient_identifier: Dict) -> Dict:
        """Get comprehensive patient overview."""
        patient = self.find_patient_by_identifier(patient_identifier)
        if not patient:
            return {"error": "Patient not found"}
        
        # Get recent visits
        patient_visits = [
            visit for visit in self.visits 
            if visit.get("patient_id") == patient["patient_id"]
        ]
        
        return {
            "patient_info": {
                "patient_id": patient["patient_id"],
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"],
                "height_cm": patient.get("height_cm"),
                "weight_kg": patient.get("weight_kg"),
                "blood_type": patient.get("blood_type"),
                "conditions": patient["conditions"],
                "medications": patient["medications"],
                "last_visit": patient["last_visit"],
                "email": patient.get("email")
            },
            "recent_visits": patient_visits[:3],  # Last 3 visits
            "total_visits": len(patient_visits),
            "whoop_connected": self.has_whoop_data(patient["name"])
        }
    
    def get_whoop_sleep_data(self, patient_identifier: Dict, days: int = 30) -> Dict:
        """Get patient's Whoop sleep data."""
        patient = self.find_patient_by_identifier(patient_identifier)
        if not patient:
            return {"error": "Patient not found"}
        
        if not self.has_whoop_data(patient["name"]):
            return {"error": self.get_whoop_not_connected_message(patient["name"])}
        
        if 'sleep' not in self.whoop_data:
            return {"error": "No Whoop sleep data available"}
        
        sleep_df = self.whoop_data['sleep']
        # Filter for this patient and limit days
        patient_sleep = sleep_df[sleep_df['Patient id'] == patient["patient_id"]].head(days)
        
        return {
            "patient_name": patient["name"],
            "period": f"Last {days} days",
            "total_records": len(patient_sleep),
            "sleep_data": patient_sleep.to_dict('records')
        }
    
    def get_whoop_activity_data(self, patient_identifier: Dict, days: int = 30) -> Dict:
        """Get patient's Whoop workout/activity data."""
        patient = self.find_patient_by_identifier(patient_identifier)
        if not patient:
            return {"error": "Patient not found"}
        
        if not self.has_whoop_data(patient["name"]):
            return {"error": self.get_whoop_not_connected_message(patient["name"])}
        
        if 'workouts' not in self.whoop_data:
            return {"error": "No Whoop workout data available"}
        
        workouts_df = self.whoop_data['workouts']
        # Filter for this patient and limit days
        patient_workouts = workouts_df[workouts_df['Patient id'] == patient["patient_id"]].head(days)
        
        return {
            "patient_name": patient["name"],
            "period": f"Last {days} days",
            "total_workouts": len(patient_workouts),
            "workout_data": patient_workouts.to_dict('records')
        }
    
    def get_whoop_physiological_cycle_data(self, patient_identifier: Dict, days: int = 30) -> Dict:
        """Get patient's Whoop physiological cycle data (recovery, strain, etc)."""
        patient = self.find_patient_by_identifier(patient_identifier)
        if not patient:
            return {"error": "Patient not found"}
        
        if not self.has_whoop_data(patient["name"]):
            return {"error": self.get_whoop_not_connected_message(patient["name"])}
        
        if 'cycles' not in self.whoop_data:
            return {"error": "No Whoop physiological cycle data available"}
        
        cycles_df = self.whoop_data['cycles']
        # Filter for this patient and limit days
        patient_cycles = cycles_df[cycles_df['Patient id'] == patient["patient_id"]].head(days)
        
        return {
            "patient_name": patient["name"],
            "period": f"Last {days} days",
            "total_cycles": len(patient_cycles),
            "cycle_data": patient_cycles.to_dict('records')
        }
    
    def get_whoop_journal_data(self, patient_identifier: Dict, days: int = 30) -> Dict:
        """Get patient's Whoop journal data."""
        patient = self.find_patient_by_identifier(patient_identifier)
        if not patient:
            return {"error": "Patient not found"}
        
        if not self.has_whoop_data(patient["name"]):
            return {"error": self.get_whoop_not_connected_message(patient["name"])}
        
        if 'journal' not in self.whoop_data:
            return {"error": "No Whoop journal data available"}
        
        journal_df = self.whoop_data['journal']
        # Filter for this patient and limit days
        patient_journal = journal_df[journal_df['Patient id'] == patient["patient_id"]].head(days)
        
        return {
            "patient_name": patient["name"],
            "period": f"Last {days} days",
            "total_entries": len(patient_journal),
            "journal_data": patient_journal.to_dict('records')
        }
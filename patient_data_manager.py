"""
Patient Data Manager - Simulates patient data storage and retrieval
In production, this would connect to EHR systems, wearables, lab systems, etc.
"""

from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Any
import json

class PatientDataManager:
    def __init__(self):
        # Simulated patient database
        self.patients = {
            "ben_smith": {
                "id": "ben_smith",
                "name": "Ben Smith",
                "age": 34,
                "gender": "male",
                "conditions": ["hypertension", "type_2_diabetes"],
                "medications": ["metformin", "lisinopril"],
                "last_visit": "2024-01-15"
            },
            "sarah_jones": {
                "id": "sarah_jones", 
                "name": "Sarah Jones",
                "age": 28,
                "gender": "female",
                "conditions": ["asthma"],
                "medications": ["albuterol"],
                "last_visit": "2024-01-20"
            },
            "mike_wilson": {
                "id": "mike_wilson",
                "name": "Mike Wilson", 
                "age": 45,
                "gender": "male",
                "conditions": ["high_cholesterol"],
                "medications": ["atorvastatin"],
                "last_visit": "2024-01-10"
            }
        }
        
        # Generate sample data
        self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate realistic sample data for demo purposes."""
        for patient_id in self.patients.keys():
            self._generate_sleep_data(patient_id)
            self._generate_vitals_data(patient_id)
            self._generate_lab_results(patient_id)
            self._generate_medication_adherence(patient_id)
            self._generate_activity_data(patient_id)
    
    def _generate_sleep_data(self, patient_id: str):
        """Generate 30 days of sleep data."""
        sleep_data = []
        base_sleep = 7.5 if patient_id == "ben_smith" else 8.0
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            # Add some realistic variation
            sleep_hours = base_sleep + random.uniform(-1.5, 1.5)
            quality = random.choice(["poor", "fair", "good", "excellent"])
            
            sleep_data.append({
                "date": date,
                "sleep_hours": round(sleep_hours, 1),
                "quality": quality,
                "bedtime": f"{random.randint(21, 23)}:{random.randint(0, 59):02d}",
                "wake_time": f"{random.randint(6, 8)}:{random.randint(0, 59):02d}"
            })
        
        self.patients[patient_id]["sleep_data"] = sleep_data
    
    def _generate_vitals_data(self, patient_id: str):
        """Generate vital signs data."""
        vitals_data = []
        
        # Different baseline vitals per patient
        if patient_id == "ben_smith":  # Has hypertension
            bp_systolic_base = 145
            bp_diastolic_base = 90
        else:
            bp_systolic_base = 120
            bp_diastolic_base = 80
        
        for i in range(10):  # Last 10 readings
            date = (datetime.now() - timedelta(days=i*3)).strftime("%Y-%m-%d")
            
            vitals_data.append({
                "date": date,
                "blood_pressure": {
                    "systolic": bp_systolic_base + random.randint(-10, 15),
                    "diastolic": bp_diastolic_base + random.randint(-5, 10)
                },
                "heart_rate": random.randint(65, 85),
                "temperature": round(98.6 + random.uniform(-0.5, 1.0), 1),
                "weight": round(170 + random.uniform(-2, 2), 1)
            })
        
        self.patients[patient_id]["vitals_data"] = vitals_data
    
    def _generate_lab_results(self, patient_id: str):
        """Generate lab results."""
        lab_data = []
        
        # Recent lab work
        for i in range(3):  # Last 3 lab visits
            date = (datetime.now() - timedelta(days=i*30)).strftime("%Y-%m-%d")
            
            if patient_id == "ben_smith":  # Diabetic
                glucose = random.randint(140, 180)
                hba1c = round(7.2 + random.uniform(-0.5, 0.8), 1)
            else:
                glucose = random.randint(80, 100)
                hba1c = round(5.4 + random.uniform(-0.2, 0.3), 1)
            
            lab_data.append({
                "date": date,
                "glucose": glucose,
                "hba1c": hba1c,
                "cholesterol": {
                    "total": random.randint(180, 220),
                    "ldl": random.randint(100, 140),
                    "hdl": random.randint(40, 60)
                },
                "kidney_function": {
                    "creatinine": round(1.0 + random.uniform(-0.2, 0.3), 1),
                    "bun": random.randint(10, 20)
                }
            })
        
        self.patients[patient_id]["lab_data"] = lab_data
    
    def _generate_medication_adherence(self, patient_id: str):
        """Generate medication adherence data."""
        adherence_data = []
        medications = self.patients[patient_id]["medications"]
        
        for med in medications:
            # Generate 30 days of adherence
            daily_adherence = []
            for i in range(30):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                taken = random.choice([True, True, True, False])  # 75% adherence
                daily_adherence.append({
                    "date": date,
                    "taken": taken,
                    "time_taken": f"{random.randint(7, 9)}:{random.randint(0, 59):02d}" if taken else None
                })
            
            adherence_data.append({
                "medication": med,
                "prescribed_dose": "As prescribed",
                "adherence_rate": round(sum(1 for d in daily_adherence if d["taken"]) / 30 * 100, 1),
                "daily_records": daily_adherence
            })
        
        self.patients[patient_id]["medication_adherence"] = adherence_data
    
    def _generate_activity_data(self, patient_id: str):
        """Generate physical activity data."""
        activity_data = []
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            activity_data.append({
                "date": date,
                "steps": random.randint(3000, 12000),
                "active_minutes": random.randint(20, 90),
                "calories_burned": random.randint(1800, 2500),
                "exercise_sessions": random.randint(0, 2)
            })
        
        self.patients[patient_id]["activity_data"] = activity_data
    
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
    
    def get_sleep_pattern(self, patient_id: str, days: int = 30) -> Dict:
        """Get patient's sleep pattern."""
        patient = self.patients.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}
        
        sleep_data = patient.get("sleep_data", [])[:days]
        
        # Calculate summary statistics
        if sleep_data:
            avg_sleep = sum(d["sleep_hours"] for d in sleep_data) / len(sleep_data)
            quality_counts = {}
            for d in sleep_data:
                quality_counts[d["quality"]] = quality_counts.get(d["quality"], 0) + 1
        else:
            avg_sleep = 0
            quality_counts = {}
        
        return {
            "patient_name": patient["name"],
            "period": f"Last {days} days",
            "average_sleep_hours": round(avg_sleep, 1),
            "sleep_quality_distribution": quality_counts,
            "recent_data": sleep_data[:7],  # Last week
            "summary": f"{patient['name']} averages {round(avg_sleep, 1)} hours of sleep per night over the past {days} days."
        }
    
    def get_vitals_summary(self, patient_id: str) -> Dict:
        """Get patient's vital signs summary."""
        patient = self.patients.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}
        
        vitals_data = patient.get("vitals_data", [])
        
        if vitals_data:
            latest = vitals_data[0]
            avg_systolic = sum(v["blood_pressure"]["systolic"] for v in vitals_data) / len(vitals_data)
            avg_diastolic = sum(v["blood_pressure"]["diastolic"] for v in vitals_data) / len(vitals_data)
        else:
            latest = {}
            avg_systolic = avg_diastolic = 0
        
        return {
            "patient_name": patient["name"],
            "latest_reading": latest,
            "average_bp": f"{round(avg_systolic)}/{round(avg_diastolic)}",
            "recent_readings": vitals_data[:5],
            "conditions": patient.get("conditions", [])
        }
    
    def get_lab_results(self, patient_id: str) -> Dict:
        """Get patient's lab results."""
        patient = self.patients.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}
        
        lab_data = patient.get("lab_data", [])
        
        return {
            "patient_name": patient["name"],
            "latest_labs": lab_data[0] if lab_data else {},
            "lab_history": lab_data,
            "conditions": patient.get("conditions", [])
        }
    
    def get_medication_adherence(self, patient_id: str) -> Dict:
        """Get patient's medication adherence."""
        patient = self.patients.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}
        
        adherence_data = patient.get("medication_adherence", [])
        
        return {
            "patient_name": patient["name"],
            "medications": adherence_data,
            "overall_adherence": round(sum(m["adherence_rate"] for m in adherence_data) / len(adherence_data), 1) if adherence_data else 0
        }
    
    def get_activity_summary(self, patient_id: str, days: int = 30) -> Dict:
        """Get patient's activity summary."""
        patient = self.patients.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}
        
        activity_data = patient.get("activity_data", [])[:days]
        
        if activity_data:
            avg_steps = sum(d["steps"] for d in activity_data) / len(activity_data)
            avg_active_minutes = sum(d["active_minutes"] for d in activity_data) / len(activity_data)
        else:
            avg_steps = avg_active_minutes = 0
        
        return {
            "patient_name": patient["name"],
            "period": f"Last {days} days",
            "average_daily_steps": round(avg_steps),
            "average_active_minutes": round(avg_active_minutes),
            "recent_activity": activity_data[:7]
        }
    
    def get_patient_overview(self, patient_id: str) -> Dict:
        """Get comprehensive patient overview."""
        patient = self.patients.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}
        
        return {
            "patient_info": {
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"],
                "conditions": patient["conditions"],
                "medications": patient["medications"],
                "last_visit": patient["last_visit"]
            },
            "recent_vitals": patient.get("vitals_data", [])[:1],
            "recent_labs": patient.get("lab_data", [])[:1],
            "sleep_summary": f"Averages {round(sum(d['sleep_hours'] for d in patient.get('sleep_data', [])[:7]) / 7, 1)} hours/night",
            "activity_summary": f"Averages {round(sum(d['steps'] for d in patient.get('activity_data', [])[:7]) / 7)} steps/day"
        }
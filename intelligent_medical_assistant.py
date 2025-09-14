"""
Intelligent Medical Assistant - Natural Language Query Processing
Handles free-form medical queries and routes to appropriate tools
"""

import pandas as pd
import json
import os
from typing import Dict, List, Optional, Any
from medical_client import MedicalClient
from patient_data_manager import PatientDataManager

class IntelligentMedicalAssistant:
    def __init__(self):
        self.medical_client = MedicalClient()
        self.patient_manager = PatientDataManager()
        self.patient_data = self._load_patient_data()
        
    def _load_patient_data(self) -> Dict[str, Any]:
        """Load patient data from doctor_data and whoop_data folders."""
        data = {}
        
        try:
            # Load doctor data
            if os.path.exists("doctor_data/patients.csv"):
                data['patients'] = pd.read_csv("doctor_data/patients.csv")
            
            if os.path.exists("doctor_data/visits.json"):
                import json
                with open("doctor_data/visits.json", 'r') as f:
                    data['visits'] = json.load(f)
            
            # Load Whoop data (Amos only)
            whoop_files = {
                'whoop_sleep': 'whoop_data/sleeps.csv',
                'whoop_workouts': 'whoop_data/workouts.csv',
                'whoop_cycles': 'whoop_data/physiological_cycles.csv',
                'whoop_journal': 'whoop_data/journal_entries.csv'
            }
            
            for key, file_path in whoop_files.items():
                if os.path.exists(file_path):
                    data[key] = pd.read_csv(file_path)
                    
        except Exception as e:
            print(f"Error loading patient data: {e}")
            
        return data
    
    async def process_query(self, query: str) -> str:
        """Process a natural language medical query."""
        
        # Create context about available data and tools
        context = self._build_context()
        
        # Enhanced prompt for intelligent routing with concise responses
        enhanced_prompt = f"""
You are a medical assistant for healthcare providers with access to patient data and medical tools.

AVAILABLE PATIENT DATA:
{context}

USER QUERY: "{query}"

RESPONSE GUIDELINES:
1. Be CONCISE and SUMMARIZED unless specifically asked for detailed information
2. For patient data queries: Provide key metrics and brief clinical insights
3. For general medical questions: Give essential information in bullet points
4. For patient-specific data: Extract relevant information with brief analysis
5. Always include brief medical disclaimers
6. Use clinical terminology appropriate for medical providers
7. If asked for "detailed" or "comprehensive" analysis, then provide full information

Provide a focused, professional response suitable for busy medical providers.
"""

        try:
            # Use the medical client to process the enhanced query
            response = await self.medical_client.query_medical_question(enhanced_prompt, "")
            
            # Post-process to add specific patient data if relevant
            enhanced_response = await self._enhance_with_patient_data(query, response)
            
            return enhanced_response
            
        except Exception as e:
            return f"I apologize, but I encountered an error processing your query: {str(e)}. Please try rephrasing your question."
    
    def _build_context(self) -> str:
        """Build context about available patient data."""
        context = []
        
        if 'patients' in self.patient_data:
            patients_df = self.patient_data['patients']
            context.append("PATIENTS IN SYSTEM:")
            for _, patient in patients_df.iterrows():
                conditions = patient.get('conditions', 'None') if pd.notna(patient.get('conditions')) else 'None'
                context.append(f"- {patient['first_name']} {patient['last_name']}, {patient['age']}yo {patient['gender']}, Conditions: {conditions}")
        
        if 'visits' in self.patient_data:
            visits = self.patient_data['visits']
            context.append(f"\nMEDICAL VISITS: {len(visits)} visits recorded")
            
        # Whoop data context (Amos only)
        if 'whoop_sleep' in self.patient_data:
            sleep_df = self.patient_data['whoop_sleep']
            context.append(f"\nWHOOP DATA AVAILABLE:")
            context.append(f"- Sleep data: {len(sleep_df)} records (Amos only)")
            
        if 'whoop_workouts' in self.patient_data:
            workouts_df = self.patient_data['whoop_workouts']
            context.append(f"- Workout data: {len(workouts_df)} sessions (Amos only)")
            
        if 'whoop_cycles' in self.patient_data:
            cycles_df = self.patient_data['whoop_cycles']
            context.append(f"- Recovery cycles: {len(cycles_df)} cycles (Amos only)")
            
        if 'whoop_journal' in self.patient_data:
            journal_df = self.patient_data['whoop_journal']
            context.append(f"- Health journal: {len(journal_df)} entries (Amos only)")
        
        return "\n".join(context)
    
    async def _enhance_with_patient_data(self, query: str, base_response: str) -> str:
        """Enhance response with specific patient data if relevant."""
        query_lower = query.lower()
        
        # Check if query is about Amos's Whoop data
        if 'amos' in query_lower and 'whoop' in query_lower:
            if 'sleep' in query_lower and 'whoop_sleep' in self.patient_data:
                sleep_data = self._format_whoop_sleep_summary()
                return f"{base_response}\n\n**Amos's Whoop Sleep Data:**\n{sleep_data}"
            elif 'workout' in query_lower and 'whoop_workouts' in self.patient_data:
                workout_data = self._format_whoop_workout_summary()
                return f"{base_response}\n\n**Amos's Whoop Workout Data:**\n{workout_data}"
        
        # Check if query is about patient visits
        if 'visit' in query_lower and 'visits' in self.patient_data:
            visits_data = self._format_visits_summary(query_lower)
            return f"{base_response}\n\n**Recent Medical Visits:**\n{visits_data}"
        
        return base_response
    
    def _format_whoop_sleep_summary(self) -> str:
        """Format Amos's Whoop sleep data summary."""
        if 'whoop_sleep' not in self.patient_data:
            return "No Whoop sleep data available."
        
        df = self.patient_data['whoop_sleep']
        recent = df.head(7)
        
        summary = []
        summary.append(f"😴 **Whoop Sleep Analysis (Last 7 Days)**")
        if not recent.empty:
            summary.append(f"• Average Sleep Performance: {recent['Sleep performance %'].mean():.1f}%")
            summary.append(f"• Average Sleep Efficiency: {recent['Sleep efficiency %'].mean():.1f}%")
            summary.append(f"• Average REM Sleep: {recent['REM duration (min)'].mean():.0f} minutes")
            summary.append(f"• Average Deep Sleep: {recent['Deep (SWS) duration (min)'].mean():.0f} minutes")
            summary.append(f"• Latest Sleep Score: {recent.iloc[0]['Sleep performance %']:.1f}%")
        
        return "\n".join(summary)
    
    def _format_whoop_workout_summary(self) -> str:
        """Format Amos's Whoop workout data summary."""
        if 'whoop_workouts' not in self.patient_data:
            return "No Whoop workout data available."
        
        df = self.patient_data['whoop_workouts']
        recent = df.head(5)
        
        summary = []
        summary.append(f"💪 **Whoop Workout Summary (Last 5 Sessions)**")
        if not recent.empty:
            summary.append(f"• Average Strain: {recent['Strain'].mean():.1f}")
            summary.append(f"• Total Workouts: {len(recent)}")
            summary.append(f"• Sports: {', '.join(recent['Sport'].unique())}")
            summary.append(f"• Latest Workout: {recent.iloc[0]['Sport']} (Strain: {recent.iloc[0]['Strain']:.1f})")
        
        return "\n".join(summary)
    
    def _format_visits_summary(self, query: str) -> str:
        """Format medical visits summary."""
        if 'visits' not in self.patient_data:
            return "No visit data available."
        
        visits = self.patient_data['visits']
        
        summary = []
        summary.append(f"🏥 **Recent Medical Visits ({len(visits)} total)**")
        
        # Show recent visits
        for visit in visits[:3]:  # Show last 3 visits
            summary.append(f"• {visit.get('visit_date', 'N/A')}: {visit.get('reason', 'N/A')} - {visit.get('diagnosis', 'N/A')}")
        
        return "\n".join(summary)
    
    def get_patient_list(self) -> List[str]:
        """Get list of available patients."""
        if 'patients' not in self.patient_data:
            return []
        
        patients = []
        for _, patient in self.patient_data['patients'].iterrows():
            patients.append(f"{patient['first_name']} {patient['last_name']}")
        
        return patients
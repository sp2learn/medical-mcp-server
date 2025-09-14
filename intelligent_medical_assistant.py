"""
Intelligent Medical Assistant - Natural Language Query Processing
Handles free-form medical queries and routes to appropriate tools
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Any
from medical_client import MedicalClient
from patient_data_manager import PatientDataManager

class IntelligentMedicalAssistant:
    def __init__(self):
        self.medical_client = MedicalClient()
        self.patient_manager = PatientDataManager()
        self.patient_data = self._load_patient_data()
        
    def _load_patient_data(self) -> Dict[str, pd.DataFrame]:
        """Load patient data from CSV files."""
        data = {}
        data_dir = "data"
        
        try:
            # Load main patient info
            if os.path.exists(f"{data_dir}/patients.csv"):
                data['patients'] = pd.read_csv(f"{data_dir}/patients.csv")
            
            # Load Ben's specific data
            if os.path.exists(f"{data_dir}/ben_sleep_data.csv"):
                data['ben_sleep'] = pd.read_csv(f"{data_dir}/ben_sleep_data.csv")
            
            if os.path.exists(f"{data_dir}/ben_vitals_data.csv"):
                data['ben_vitals'] = pd.read_csv(f"{data_dir}/ben_vitals_data.csv")
                
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
                context.append(f"- {patient['first_name']} {patient['last_name']}, {patient['age']}yo {patient['gender']}, Conditions: {patient['conditions']}")
        
        if 'ben_sleep' in self.patient_data:
            sleep_df = self.patient_data['ben_sleep']
            recent_sleep = sleep_df.head(7)  # Last 7 days
            avg_sleep = recent_sleep['sleep_hours'].mean()
            context.append(f"\nBEN'S RECENT SLEEP DATA (last 7 days):")
            context.append(f"- Average sleep: {avg_sleep:.1f} hours/night")
            context.append(f"- Sleep quality distribution: {recent_sleep['sleep_quality'].value_counts().to_dict()}")
            context.append(f"- Latest sleep: {recent_sleep.iloc[0]['sleep_hours']} hours on {recent_sleep.iloc[0]['date']}")
        
        if 'ben_vitals' in self.patient_data:
            vitals_df = self.patient_data['ben_vitals']
            latest_vitals = vitals_df.iloc[0]
            context.append(f"\nBEN'S RECENT VITALS:")
            context.append(f"- Latest BP: {latest_vitals['systolic_bp']}/{latest_vitals['diastolic_bp']} mmHg")
            context.append(f"- Heart rate: {latest_vitals['heart_rate']} bpm")
            context.append(f"- Weight: {latest_vitals['weight_kg']} kg")
            context.append(f"- Glucose: {latest_vitals['glucose_mg_dl']} mg/dL")
        
        return "\n".join(context)
    
    async def _enhance_with_patient_data(self, query: str, base_response: str) -> str:
        """Enhance response with specific patient data if relevant."""
        query_lower = query.lower()
        
        # Check if query is about Ben's sleep
        if 'ben' in query_lower and 'sleep' in query_lower and 'ben_sleep' in self.patient_data:
            sleep_data = self._format_sleep_summary()
            return f"{base_response}\n\n**Ben's Current Sleep Data:**\n{sleep_data}"
        
        # Check if query is about Ben's vitals
        if 'ben' in query_lower and ('vital' in query_lower or 'blood pressure' in query_lower or 'bp' in query_lower) and 'ben_vitals' in self.patient_data:
            vitals_data = self._format_vitals_summary()
            return f"{base_response}\n\n**Ben's Current Vital Signs:**\n{vitals_data}"
        
        return base_response
    
    def _format_sleep_summary(self) -> str:
        """Format Ben's sleep data summary."""
        if 'ben_sleep' not in self.patient_data:
            return "No sleep data available."
        
        df = self.patient_data['ben_sleep']
        recent = df.head(7)
        
        summary = []
        summary.append(f"📊 **Sleep Analysis (Last 7 Days)**")
        summary.append(f"• Average Sleep Duration: {recent['sleep_hours'].mean():.1f} hours")
        summary.append(f"• Sleep Efficiency: {recent['sleep_efficiency'].mean():.1f}%")
        summary.append(f"• Average Deep Sleep: {recent['deep_sleep_minutes'].mean():.0f} minutes")
        summary.append(f"• Average REM Sleep: {recent['rem_sleep_minutes'].mean():.0f} minutes")
        summary.append(f"• Quality Distribution: {dict(recent['sleep_quality'].value_counts())}")
        summary.append(f"• Latest Night: {recent.iloc[0]['sleep_hours']} hours ({recent.iloc[0]['sleep_quality']} quality)")
        
        return "\n".join(summary)
    
    def _format_vitals_summary(self) -> str:
        """Format Ben's vitals data summary."""
        if 'ben_vitals' not in self.patient_data:
            return "No vitals data available."
        
        df = self.patient_data['ben_vitals']
        recent = df.head(5)
        latest = df.iloc[0]
        
        summary = []
        summary.append(f"🩺 **Vital Signs Summary (Last 5 Readings)**")
        summary.append(f"• Latest BP: {latest['systolic_bp']}/{latest['diastolic_bp']} mmHg ({latest['date']})")
        summary.append(f"• Average BP: {recent['systolic_bp'].mean():.0f}/{recent['diastolic_bp'].mean():.0f} mmHg")
        summary.append(f"• Heart Rate: {latest['heart_rate']} bpm (avg: {recent['heart_rate'].mean():.0f})")
        summary.append(f"• Weight: {latest['weight_kg']} kg")
        summary.append(f"• Latest Glucose: {latest['glucose_mg_dl']} mg/dL")
        summary.append(f"• BP Trend: {'↑ Elevated' if recent['systolic_bp'].mean() > 140 else '✓ Normal'}")
        
        return "\n".join(summary)
    
    def get_patient_list(self) -> List[str]:
        """Get list of available patients."""
        if 'patients' not in self.patient_data:
            return []
        
        patients = []
        for _, patient in self.patient_data['patients'].iterrows():
            patients.append(f"{patient['first_name']} {patient['last_name']}")
        
        return patients
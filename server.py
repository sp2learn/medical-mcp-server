#!/usr/bin/env python3
"""
Medical Query MCP Server
Provides medical information responses using Gemini or AWS Nova
"""

import asyncio
import os
from typing import Any, Sequence
from dotenv import load_dotenv

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

from medical_client import MedicalClient
from patient_data_manager import PatientDataManager
from tool_config import tool_config

# Load environment variables
load_dotenv()

# Initialize the MCP server
server = Server("medical-query-server")

# Initialize medical client and patient data manager
medical_client = MedicalClient()
patient_manager = PatientDataManager()

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available medical query tools."""
    return tool_config.get_enabled_tools()

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls for medical queries."""
    
    if name == "medical_query":
        question = arguments.get("question", "")
        context = arguments.get("context", "")
        
        if not question:
            return [types.TextContent(
                type="text",
                text="Error: No question provided"
            )]
        
        try:
            response = await medical_client.query_medical_question(question, context)
            return [types.TextContent(
                type="text", 
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error processing medical query: {str(e)}"
            )]
    
    elif name == "symptom_checker":
        symptoms = arguments.get("symptoms", [])
        age = arguments.get("age")
        gender = arguments.get("gender")
        
        if not symptoms:
            return [types.TextContent(
                type="text",
                text="Error: No symptoms provided"
            )]
        
        try:
            response = await medical_client.analyze_symptoms(symptoms, age, gender)
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text", 
                text=f"Error analyzing symptoms: {str(e)}"
            )]
    
    elif name == "get_patient_sleep_pattern":
        patient_identifier = arguments.get("patient_identifier", "")
        days = arguments.get("days", 30)
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            # Find patient
            patient = patient_manager.find_patient(patient_identifier)
            if not patient:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Patient '{patient_identifier}' not found. Available patients: Ben Smith, Sarah Jones, Mike Wilson"
                )]
            
            # Get sleep data
            sleep_data = patient_manager.get_sleep_pattern(patient["id"], days)
            
            # Format response
            response = f"Sleep Pattern Analysis for {sleep_data['patient_name']}\n"
            response += f"Period: {sleep_data['period']}\n"
            response += f"Average Sleep: {sleep_data['average_sleep_hours']} hours per night\n\n"
            response += f"Sleep Quality Distribution:\n"
            for quality, count in sleep_data['sleep_quality_distribution'].items():
                response += f"  {quality.title()}: {count} nights\n"
            response += f"\nSummary: {sleep_data['summary']}"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving sleep data: {str(e)}"
            )]
    
    elif name == "get_patient_vitals":
        patient_identifier = arguments.get("patient_identifier", "")
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            patient = patient_manager.find_patient(patient_identifier)
            if not patient:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Patient '{patient_identifier}' not found"
                )]
            
            vitals_data = patient_manager.get_vitals_summary(patient["id"])
            
            response = f"Vital Signs Summary for {vitals_data['patient_name']}\n\n"
            if vitals_data['latest_reading']:
                latest = vitals_data['latest_reading']
                response += f"Latest Reading ({latest['date']}):\n"
                response += f"  Blood Pressure: {latest['blood_pressure']['systolic']}/{latest['blood_pressure']['diastolic']} mmHg\n"
                response += f"  Heart Rate: {latest['heart_rate']} bpm\n"
                response += f"  Temperature: {latest['temperature']}°F\n"
                response += f"  Weight: {latest['weight']} lbs\n\n"
            
            response += f"Average BP: {vitals_data['average_bp']} mmHg\n"
            response += f"Known Conditions: {', '.join(vitals_data['conditions'])}"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving vitals: {str(e)}"
            )]
    
    elif name == "get_patient_labs":
        patient_identifier = arguments.get("patient_identifier", "")
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            patient = patient_manager.find_patient(patient_identifier)
            if not patient:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Patient '{patient_identifier}' not found"
                )]
            
            lab_data = patient_manager.get_lab_results(patient["id"])
            
            response = f"Laboratory Results for {lab_data['patient_name']}\n\n"
            if lab_data['latest_labs']:
                latest = lab_data['latest_labs']
                response += f"Latest Labs ({latest['date']}):\n"
                response += f"  Glucose: {latest['glucose']} mg/dL\n"
                response += f"  HbA1c: {latest['hba1c']}%\n"
                response += f"  Total Cholesterol: {latest['cholesterol']['total']} mg/dL\n"
                response += f"  LDL: {latest['cholesterol']['ldl']} mg/dL\n"
                response += f"  HDL: {latest['cholesterol']['hdl']} mg/dL\n"
                response += f"  Creatinine: {latest['kidney_function']['creatinine']} mg/dL\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving lab results: {str(e)}"
            )]
    
    elif name == "get_medication_adherence":
        patient_identifier = arguments.get("patient_identifier", "")
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            patient = patient_manager.find_patient(patient_identifier)
            if not patient:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Patient '{patient_identifier}' not found"
                )]
            
            adherence_data = patient_manager.get_medication_adherence(patient["id"])
            
            response = f"Medication Adherence for {adherence_data['patient_name']}\n\n"
            response += f"Overall Adherence Rate: {adherence_data['overall_adherence']}%\n\n"
            
            for med in adherence_data['medications']:
                response += f"{med['medication'].title()}:\n"
                response += f"  Adherence Rate: {med['adherence_rate']}%\n"
                response += f"  Prescribed: {med['prescribed_dose']}\n\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving medication data: {str(e)}"
            )]
    
    elif name == "get_patient_activity":
        patient_identifier = arguments.get("patient_identifier", "")
        days = arguments.get("days", 30)
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            patient = patient_manager.find_patient(patient_identifier)
            if not patient:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Patient '{patient_identifier}' not found"
                )]
            
            activity_data = patient_manager.get_activity_summary(patient["id"], days)
            
            response = f"Physical Activity Summary for {activity_data['patient_name']}\n"
            response += f"Period: {activity_data['period']}\n\n"
            response += f"Average Daily Steps: {activity_data['average_daily_steps']:,}\n"
            response += f"Average Active Minutes: {activity_data['average_active_minutes']} minutes/day\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving activity data: {str(e)}"
            )]
    
    elif name == "get_patient_overview":
        patient_identifier = arguments.get("patient_identifier", "")
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            patient = patient_manager.find_patient(patient_identifier)
            if not patient:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Patient '{patient_identifier}' not found"
                )]
            
            overview = patient_manager.get_patient_overview(patient["id"])
            info = overview['patient_info']
            
            response = f"Patient Overview: {info['name']}\n\n"
            response += f"Demographics:\n"
            response += f"  Age: {info['age']} years\n"
            response += f"  Gender: {info['gender'].title()}\n"
            response += f"  Last Visit: {info['last_visit']}\n\n"
            response += f"Conditions: {', '.join(info['conditions'])}\n"
            response += f"Medications: {', '.join(info['medications'])}\n\n"
            response += f"Recent Summary:\n"
            response += f"  Sleep: {overview['sleep_summary']}\n"
            response += f"  Activity: {overview['activity_summary']}\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving patient overview: {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="medical-query-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
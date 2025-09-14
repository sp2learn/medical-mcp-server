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
    
    if name == "get_patient_visits":
        patient_identifier = arguments.get("patient_identifier", {})
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            visits_data = patient_manager.get_patient_visits(patient_identifier)
            
            if "error" in visits_data:
                return [types.TextContent(
                    type="text",
                    text=visits_data["error"]
                )]
            
            response = f"Visit History for {visits_data['patient_name']}\n"
            response += f"Total Visits: {visits_data['total_visits']}\n\n"
            
            for visit in visits_data['visits'][:5]:  # Show last 5 visits
                response += f"Visit Date: {visit.get('visit_date', 'N/A')}\n"
                response += f"Type: {visit.get('visit_type', 'N/A')}\n"
                response += f"Reason: {visit.get('reason', 'N/A')}\n"
                response += f"Diagnosis: {visit.get('diagnosis', 'N/A')}\n"
                if 'vitals' in visit:
                    vitals = visit['vitals']
                    response += f"Vitals: BP {vitals.get('systolic_bp', 'N/A')}/{vitals.get('diastolic_bp', 'N/A')}, HR {vitals.get('heart_rate', 'N/A')}\n"
                response += "\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving visit data: {str(e)}"
            )]
    
    elif name == "get_patient_overview":
        patient_identifier = arguments.get("patient_identifier", {})
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            overview = patient_manager.get_patient_overview(patient_identifier)
            
            if "error" in overview:
                return [types.TextContent(
                    type="text",
                    text=overview["error"]
                )]
            
            info = overview['patient_info']
            
            response = f"Patient Overview: {info['name']}\n\n"
            response += f"Demographics:\n"
            response += f"  Patient ID: {info['patient_id']}\n"
            response += f"  Age: {info['age']} years\n"
            response += f"  Gender: {info['gender'].title()}\n"
            response += f"  Height: {info.get('height_cm', 'N/A')} cm\n"
            response += f"  Weight: {info.get('weight_kg', 'N/A')} kg\n"
            response += f"  Blood Type: {info.get('blood_type', 'N/A')}\n"
            response += f"  Email: {info.get('email', 'N/A')}\n"
            response += f"  Last Visit: {info['last_visit']}\n\n"
            response += f"Conditions: {', '.join(info['conditions']) if info['conditions'] else 'None'}\n"
            response += f"Medications: {', '.join(info['medications']) if info['medications'] else 'None'}\n\n"
            response += f"Total Visits: {overview['total_visits']}\n"
            response += f"Whoop Connected: {'Yes' if overview['whoop_connected'] else 'No'}\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving patient overview: {str(e)}"
            )]
    
    elif name == "get_patient_whoop_sleep_data":
        patient_identifier = arguments.get("patient_identifier", {})
        days = arguments.get("days", 30)
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            sleep_data = patient_manager.get_whoop_sleep_data(patient_identifier, days)
            
            if "error" in sleep_data:
                return [types.TextContent(
                    type="text",
                    text=sleep_data["error"]
                )]
            
            response = f"Whoop Sleep Data for {sleep_data['patient_name']}\n"
            response += f"Period: {sleep_data['period']}\n"
            response += f"Total Records: {sleep_data['total_records']}\n\n"
            
            # Show summary of recent sleep data
            if sleep_data['sleep_data']:
                recent_sleeps = sleep_data['sleep_data'][:5]  # Last 5 nights
                response += "Recent Sleep Performance:\n"
                for sleep in recent_sleeps:
                    response += f"  {sleep.get('Cycle start time', 'N/A')}: {sleep.get('Sleep performance %', 'N/A')}% performance, "
                    response += f"{sleep.get('Asleep duration (min)', 'N/A')} min sleep\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving Whoop sleep data: {str(e)}"
            )]
    
    elif name == "get_patient_whoop_activity_data":
        patient_identifier = arguments.get("patient_identifier", {})
        days = arguments.get("days", 30)
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            activity_data = patient_manager.get_whoop_activity_data(patient_identifier, days)
            
            if "error" in activity_data:
                return [types.TextContent(
                    type="text",
                    text=activity_data["error"]
                )]
            
            response = f"Whoop Activity Data for {activity_data['patient_name']}\n"
            response += f"Period: {activity_data['period']}\n"
            response += f"Total Workouts: {activity_data['total_workouts']}\n\n"
            
            # Show summary of recent workouts
            if activity_data['workout_data']:
                recent_workouts = activity_data['workout_data'][:5]  # Last 5 workouts
                response += "Recent Workouts:\n"
                for workout in recent_workouts:
                    response += f"  {workout.get('Activity name', 'N/A')}: Strain {workout.get('Activity Strain', 'N/A')}, "
                    response += f"{workout.get('Duration (min)', 'N/A')} min\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving Whoop activity data: {str(e)}"
            )]
    
    elif name == "get_patient_whoop_physiological_cycle_data":
        patient_identifier = arguments.get("patient_identifier", {})
        days = arguments.get("days", 30)
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            cycle_data = patient_manager.get_whoop_physiological_cycle_data(patient_identifier, days)
            
            if "error" in cycle_data:
                return [types.TextContent(
                    type="text",
                    text=cycle_data["error"]
                )]
            
            response = f"Whoop Physiological Cycle Data for {cycle_data['patient_name']}\n"
            response += f"Period: {cycle_data['period']}\n"
            response += f"Total Cycles: {cycle_data['total_cycles']}\n\n"
            
            # Show summary of recent cycles
            if cycle_data['cycle_data']:
                recent_cycles = cycle_data['cycle_data'][:5]  # Last 5 cycles
                response += "Recent Recovery & Strain:\n"
                for cycle in recent_cycles:
                    response += f"  {cycle.get('Cycle start time', 'N/A')}: Recovery {cycle.get('Recovery score %', 'N/A')}%, "
                    response += f"Strain {cycle.get('Day Strain', 'N/A')}\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving Whoop cycle data: {str(e)}"
            )]
    
    elif name == "get_patient_whoop_journal_data":
        patient_identifier = arguments.get("patient_identifier", {})
        days = arguments.get("days", 30)
        
        if not patient_identifier:
            return [types.TextContent(
                type="text",
                text="Error: Patient identifier required"
            )]
        
        try:
            journal_data = patient_manager.get_whoop_journal_data(patient_identifier, days)
            
            if "error" in journal_data:
                return [types.TextContent(
                    type="text",
                    text=journal_data["error"]
                )]
            
            response = f"Whoop Journal Data for {journal_data['patient_name']}\n"
            response += f"Period: {journal_data['period']}\n"
            response += f"Total Entries: {journal_data['total_entries']}\n\n"
            
            # Show summary of recent journal entries
            if journal_data['journal_data']:
                recent_entries = journal_data['journal_data'][:5]  # Last 5 entries
                response += "Recent Journal Entries:\n"
                for entry in recent_entries:
                    answer = "Yes" if entry.get('Answered yes', False) else "No"
                    response += f"  {entry.get('Cycle start time', 'N/A')}: {entry.get('Question text', 'N/A')} - {answer}\n"
            
            return [types.TextContent(
                type="text",
                text=response
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving Whoop journal data: {str(e)}"
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
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

# Load environment variables
load_dotenv()

# Initialize the MCP server
server = Server("medical-query-server")

# Initialize medical client
medical_client = MedicalClient()

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available medical query tools."""
    return [
        Tool(
            name="medical_query",
            description="Answer medical questions with professional, evidence-based responses",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The medical question to answer"
                    },
                    "context": {
                        "type": "string", 
                        "description": "Additional context or patient information (optional)",
                        "default": ""
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="symptom_checker",
            description="Analyze symptoms and provide general guidance (not a diagnosis)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symptoms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of symptoms to analyze"
                    },
                    "age": {
                        "type": "integer",
                        "description": "Patient age (optional)",
                        "minimum": 0,
                        "maximum": 120
                    },
                    "gender": {
                        "type": "string",
                        "description": "Patient gender (optional)",
                        "enum": ["male", "female", "other"]
                    }
                },
                "required": ["symptoms"]
            }
        )
    ]

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
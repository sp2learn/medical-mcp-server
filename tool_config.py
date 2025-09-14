"""
MCP Tool Configuration - Centralized tool definitions and settings
"""

from mcp.types import Tool
from typing import List, Dict, Any

class ToolConfig:
    """Centralized configuration for MCP tools."""
    
    def __init__(self):
        self.tools = {}
        self.tool_categories = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all tool configurations."""
        
        # General Medical Tools
        self.tools["medical_query"] = {
            "definition": Tool(
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
            "category": "general",
            "enabled": True,
            "rate_limit": 10,  # requests per minute
            "requires_auth": True
        }
        
        self.tools["symptom_checker"] = {
            "definition": Tool(
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
            ),
            "category": "general",
            "enabled": True,
            "rate_limit": 15,
            "requires_auth": True
        }
        
        # Patient Data Tools
        self.tools["get_patient_sleep_pattern"] = {
            "definition": Tool(
                name="get_patient_sleep_pattern",
                description="Get a patient's sleep pattern and analysis for specified time period",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_identifier": {
                            "type": "string",
                            "description": "Patient name or ID (e.g., 'Ben Smith' or 'ben_smith')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze (default: 30)",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 90
                        }
                    },
                    "required": ["patient_identifier"]
                }
            ),
            "category": "patient_data",
            "enabled": True,
            "rate_limit": 20,
            "requires_auth": True,
            "requires_patient_access": True
        }
        
        self.tools["get_patient_vitals"] = {
            "definition": Tool(
                name="get_patient_vitals",
                description="Get a patient's vital signs summary and recent readings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_identifier": {
                            "type": "string",
                            "description": "Patient name or ID (e.g., 'Ben Smith' or 'ben_smith')"
                        }
                    },
                    "required": ["patient_identifier"]
                }
            ),
            "category": "patient_data",
            "enabled": True,
            "rate_limit": 20,
            "requires_auth": True,
            "requires_patient_access": True
        }
        
        self.tools["get_patient_labs"] = {
            "definition": Tool(
                name="get_patient_labs",
                description="Get a patient's laboratory results and trends",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_identifier": {
                            "type": "string",
                            "description": "Patient name or ID (e.g., 'Ben Smith' or 'ben_smith')"
                        }
                    },
                    "required": ["patient_identifier"]
                }
            ),
            "category": "patient_data",
            "enabled": True,
            "rate_limit": 15,
            "requires_auth": True,
            "requires_patient_access": True
        }
        
        self.tools["get_medication_adherence"] = {
            "definition": Tool(
                name="get_medication_adherence",
                description="Get a patient's medication adherence data and compliance rates",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_identifier": {
                            "type": "string",
                            "description": "Patient name or ID (e.g., 'Ben Smith' or 'ben_smith')"
                        }
                    },
                    "required": ["patient_identifier"]
                }
            ),
            "category": "patient_data",
            "enabled": True,
            "rate_limit": 15,
            "requires_auth": True,
            "requires_patient_access": True
        }
        
        self.tools["get_patient_activity"] = {
            "definition": Tool(
                name="get_patient_activity",
                description="Get a patient's physical activity summary and trends",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_identifier": {
                            "type": "string",
                            "description": "Patient name or ID (e.g., 'Ben Smith' or 'ben_smith')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze (default: 30)",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 90
                        }
                    },
                    "required": ["patient_identifier"]
                }
            ),
            "category": "patient_data",
            "enabled": True,
            "rate_limit": 20,
            "requires_auth": True,
            "requires_patient_access": True
        }
        
        self.tools["get_patient_overview"] = {
            "definition": Tool(
                name="get_patient_overview",
                description="Get comprehensive patient overview including demographics, conditions, and recent data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_identifier": {
                            "type": "string",
                            "description": "Patient name or ID (e.g., 'Ben Smith' or 'ben_smith')"
                        }
                    },
                    "required": ["patient_identifier"]
                }
            ),
            "category": "patient_data",
            "enabled": True,
            "rate_limit": 10,
            "requires_auth": True,
            "requires_patient_access": True
        }
        
        # Set up categories
        self.tool_categories = {
            "general": ["medical_query", "symptom_checker"],
            "patient_data": [
                "get_patient_sleep_pattern", "get_patient_vitals", "get_patient_labs",
                "get_medication_adherence", "get_patient_activity", "get_patient_overview"
            ]
        }
    
    def get_enabled_tools(self) -> List[Tool]:
        """Get all enabled tool definitions."""
        return [
            config["definition"] 
            for config in self.tools.values() 
            if config.get("enabled", True)
        ]
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get tools by category."""
        tool_names = self.tool_categories.get(category, [])
        return [
            self.tools[name]["definition"] 
            for name in tool_names 
            if self.tools[name].get("enabled", True)
        ]
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool."""
        return self.tools.get(tool_name, {})
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled."""
        return self.tools.get(tool_name, {}).get("enabled", False)
    
    def get_rate_limit(self, tool_name: str) -> int:
        """Get rate limit for a tool."""
        return self.tools.get(tool_name, {}).get("rate_limit", 10)
    
    def requires_auth(self, tool_name: str) -> bool:
        """Check if tool requires authentication."""
        return self.tools.get(tool_name, {}).get("requires_auth", True)
    
    def requires_patient_access(self, tool_name: str) -> bool:
        """Check if tool requires patient data access."""
        return self.tools.get(tool_name, {}).get("requires_patient_access", False)
    
    def add_tool(self, tool_name: str, tool_config: Dict[str, Any]):
        """Add a new tool configuration."""
        self.tools[tool_name] = tool_config
        
        # Add to category if specified
        category = tool_config.get("category", "general")
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        if tool_name not in self.tool_categories[category]:
            self.tool_categories[category].append(tool_name)
    
    def disable_tool(self, tool_name: str):
        """Disable a tool."""
        if tool_name in self.tools:
            self.tools[tool_name]["enabled"] = False
    
    def enable_tool(self, tool_name: str):
        """Enable a tool."""
        if tool_name in self.tools:
            self.tools[tool_name]["enabled"] = True
    
    def get_tool_summary(self) -> Dict[str, Any]:
        """Get summary of all tools and their status."""
        summary = {
            "total_tools": len(self.tools),
            "enabled_tools": len([t for t in self.tools.values() if t.get("enabled", True)]),
            "categories": {},
            "tools": {}
        }
        
        for category, tool_names in self.tool_categories.items():
            summary["categories"][category] = {
                "total": len(tool_names),
                "enabled": len([name for name in tool_names if self.tools[name].get("enabled", True)])
            }
        
        for tool_name, config in self.tools.items():
            summary["tools"][tool_name] = {
                "enabled": config.get("enabled", True),
                "category": config.get("category", "general"),
                "rate_limit": config.get("rate_limit", 10),
                "requires_auth": config.get("requires_auth", True)
            }
        
        return summary

# Global tool configuration instance
tool_config = ToolConfig()
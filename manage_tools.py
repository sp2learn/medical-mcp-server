#!/usr/bin/env python3
"""
Tool Management Utility for Medical MCP Server
"""

import json
from tool_config import tool_config

def list_tools():
    """List all available tools."""
    print("🔧 Medical MCP Server - Tool Configuration")
    print("=" * 50)
    
    summary = tool_config.get_tool_summary()
    
    print(f"Total Tools: {summary['total_tools']}")
    print(f"Enabled Tools: {summary['enabled_tools']}")
    print()
    
    for category, info in summary['categories'].items():
        print(f"📂 {category.upper()} ({info['enabled']}/{info['total']} enabled)")
        
        category_tools = tool_config.tool_categories[category]
        for tool_name in category_tools:
            config = tool_config.get_tool_config(tool_name)
            status = "✅" if config.get("enabled", True) else "❌"
            rate_limit = config.get("rate_limit", 10)
            print(f"  {status} {tool_name} (rate: {rate_limit}/min)")
        print()

def enable_tool(tool_name: str):
    """Enable a specific tool."""
    if tool_name in tool_config.tools:
        tool_config.enable_tool(tool_name)
        print(f"✅ Enabled tool: {tool_name}")
    else:
        print(f"❌ Tool not found: {tool_name}")

def disable_tool(tool_name: str):
    """Disable a specific tool."""
    if tool_name in tool_config.tools:
        tool_config.disable_tool(tool_name)
        print(f"❌ Disabled tool: {tool_name}")
    else:
        print(f"❌ Tool not found: {tool_name}")

def show_tool_details(tool_name: str):
    """Show detailed information about a tool."""
    config = tool_config.get_tool_config(tool_name)
    if not config:
        print(f"❌ Tool not found: {tool_name}")
        return
    
    print(f"🔧 Tool Details: {tool_name}")
    print("-" * 30)
    print(f"Description: {config['definition'].description}")
    print(f"Category: {config.get('category', 'general')}")
    print(f"Enabled: {config.get('enabled', True)}")
    print(f"Rate Limit: {config.get('rate_limit', 10)}/min")
    print(f"Requires Auth: {config.get('requires_auth', True)}")
    print(f"Requires Patient Access: {config.get('requires_patient_access', False)}")
    print()
    print("Input Schema:")
    schema = config['definition'].inputSchema
    for prop, details in schema.get('properties', {}).items():
        required = prop in schema.get('required', [])
        req_marker = "*" if required else ""
        print(f"  {prop}{req_marker}: {details.get('type', 'unknown')} - {details.get('description', 'No description')}")

def add_custom_tool():
    """Interactive tool to add a custom tool."""
    print("🔧 Add Custom Tool")
    print("-" * 20)
    
    tool_name = input("Tool name: ")
    description = input("Description: ")
    category = input("Category (general/patient_data/custom): ") or "custom"
    
    # Simple tool configuration
    from mcp.types import Tool
    
    new_tool_config = {
        "definition": Tool(
            name=tool_name,
            description=description,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query parameter"
                    }
                },
                "required": ["query"]
            }
        ),
        "category": category,
        "enabled": True,
        "rate_limit": 10,
        "requires_auth": True
    }
    
    tool_config.add_tool(tool_name, new_tool_config)
    print(f"✅ Added custom tool: {tool_name}")

def main():
    """Main CLI interface."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python manage_tools.py <command> [args]")
        print("Commands:")
        print("  list                    - List all tools")
        print("  enable <tool_name>      - Enable a tool")
        print("  disable <tool_name>     - Disable a tool")
        print("  details <tool_name>     - Show tool details")
        print("  add                     - Add custom tool (interactive)")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_tools()
    elif command == "enable" and len(sys.argv) > 2:
        enable_tool(sys.argv[2])
    elif command == "disable" and len(sys.argv) > 2:
        disable_tool(sys.argv[2])
    elif command == "details" and len(sys.argv) > 2:
        show_tool_details(sys.argv[2])
    elif command == "add":
        add_custom_tool()
    else:
        print("Invalid command or missing arguments")

if __name__ == "__main__":
    main()
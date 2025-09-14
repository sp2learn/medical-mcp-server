# Medical Query MCP Server

A Model Context Protocol (MCP) server that provides medical information responses using Gemini or AWS Nova as the backend.

## Features

- Medical query processing
- Support for Gemini and AWS Nova models
- Easy deployment and configuration
- MCP-compliant server implementation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API keys in `.env`:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the server:
```bash
python server.py
```

## Usage

Add to your MCP client configuration:
```json
{
  "mcpServers": {
    "medical-query": {
      "command": "python",
      "args": ["path/to/medical-mcp-server/server.py"],
      "env": {
        "MEDICAL_MODEL": "gemini"
      }
    }
  }
}
```
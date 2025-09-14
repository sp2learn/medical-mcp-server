#!/bin/bash
# Medical MCP Server Test Runner

echo "🧪 Medical MCP Server Test Suite"
echo "================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your API keys."
    echo "   Copy .env.example to .env and add your keys."
    exit 1
fi

echo "✓ Environment ready"
echo ""

# Run tests
echo "🚀 Running dry run test..."
python dry_run_test.py
echo ""

echo "🚀 Running startup test..."
python startup_test.py
echo ""

echo "🚀 Running full API test..."
python test_server.py
echo ""

echo "🎉 All tests completed!"
echo ""
echo "To start the MCP server:"
echo "  python server.py"
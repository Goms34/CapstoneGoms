#!/bin/bash

# Loan Approval System Startup Script

echo "======================================"
echo "Loan Approval System - Startup"
echo "======================================"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e . > /dev/null 2>&1

echo ""
echo "✅ System ready to start"
echo ""
echo "Run the following in separate terminals:"
echo ""
echo "1. Start FastAPI server:"
echo "   python -m uvicorn api.main:app --reload --port 8000"
echo ""
echo "2. Start Streamlit UI:"
echo "   streamlit run ui/app.py"
echo ""
echo "Make sure ANTHROPIC_API_KEY is set in your environment."
echo ""

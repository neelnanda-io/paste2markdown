#!/bin/bash

echo "Setting up paste2mark..."

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting paste2mark..."
echo "Press Option+V to paste clipboard content as markdown"
echo "Press Ctrl+C to stop"
echo ""
python3 paste2mark.py
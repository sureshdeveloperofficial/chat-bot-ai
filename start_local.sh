#!/bin/bash

echo "🚀 Starting Microservice Chatbot Locally (Linux/macOS)"
echo "====================================================="

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo "❌ Virtual environment not found. Please run ./install_local.sh first."
    exit 1
fi

# Activate virtual environment and run startup script
venv/bin/python start_local.py
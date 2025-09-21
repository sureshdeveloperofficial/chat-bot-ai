#!/bin/bash

echo "🚀 Installing Microservice Chatbot Locally (Linux/macOS)"
echo "======================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ required. Current version: $python_version"
    exit 1
fi

# Make the script executable
chmod +x install_local.py
chmod +x start_local.py

# Run the Python installation script
python3 install_local.py

echo ""
echo "📋 Installation complete! Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: ./start_local.sh"
echo ""
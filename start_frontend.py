#!/usr/bin/env python3
"""
Start the Streamlit frontend
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Streamlit Frontend...")
    
    # Change to frontend directory
    frontend_dir = "frontend"
    
    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found!")
        return
    
    try:
        # Start Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"]
        
        print("📱 Frontend will be available at: http://localhost:8501")
        print("⚠️  Keep this window open while using the frontend")
        print("Press Ctrl+C to stop the frontend")
        
        subprocess.run(cmd, cwd=frontend_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
Simple server startup script for PNP Inventory System
"""

import os
import sys
import subprocess
import time

def start_server():
    """Start the Django development server"""
    print("🚀 Starting PNP Inventory System Server...")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run from the project root directory.")
        return
    
    print("📁 Current directory:", os.getcwd())
    print("🔧 Server command: python manage.py runserver 0.0.0.0:8000")
    print("🌐 Local access: http://127.0.0.1:8000")
    print("🌐 LAN access: http://192.168.1.43:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
        print("🚀 Server starting...")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running: python manage.py runserver 0.0.0.0:8000")

if __name__ == "__main__":
    start_server()

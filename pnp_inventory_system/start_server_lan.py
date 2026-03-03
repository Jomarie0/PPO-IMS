import subprocess
import sys
import os

def start_server():
    print("Starting PNP Inventory System for LAN Access...")
    print("=" * 50)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
        print("Server starting on: http://0.0.0.0:8000")
        print("Other devices can access via your local IP")
        print("Press Ctrl+C to stop server")
        print("=" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()

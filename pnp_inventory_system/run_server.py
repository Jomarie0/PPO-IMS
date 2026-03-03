#!/usr/bin/env python
"""
Run Django server with proper configuration checks
"""

import os
import sys
import subprocess
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_configuration():
    """Check Django configuration"""
    print("🔍 Checking PNP System Configuration...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found!")
        print("💡 Please run this script from the project root directory")
        return False
    
    print("✅ Found manage.py - in correct directory")
    
    # Check ALLOWED_HOSTS
    try:
        with open('config/settings.py', 'r') as f:
            content = f.read()
            if 'ALLOWED_HOSTS' in content:
                print("✅ ALLOWED_HOSTS found in settings")
                # Extract the ALLOWED_HOSTS list
                import re
                match = re.search(r'ALLOWED_HOSTS = \[(.*?)\]', content)
                if match:
                    hosts = eval(match.group(1))
                    print(f"📋 Configured hosts: {hosts}")
                    
                    # Check if wildcard is included
                    if '*' in hosts:
                        print("✅ Wildcard '*' included - allows any host")
                    else:
                        print("⚠️  No wildcard found - only specific hosts allowed")
                    
                    # Check if local IP is included
                    local_ip = get_local_ip()
                    if local_ip in hosts:
                        print(f"✅ Local IP {local_ip} is allowed")
                    else:
                        print(f"⚠️  Local IP {local_ip} is NOT in ALLOWED_HOSTS")
            else:
                print("❌ ALLOWED_HOSTS not found in settings")
                return False
    except Exception as e:
        print(f"❌ Error reading settings.py: {e}")
        return False
    
    return True

def start_server():
    """Start the Django development server"""
    if not check_configuration():
        return
    
    print("\n🚀 Starting PNP Inventory System Server...")
    print("=" * 50)
    
    local_ip = get_local_ip()
    print(f"🌐 Local IP: {local_ip}")
    print(f"🔗 Server URL: http://0.0.0.0:8000")
    print(f"🌐 LAN URL: http://{local_ip}:8000")
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
        print("\n💡 Troubleshooting:")
        print("   1. Make sure you're in the project root directory")
        print("   2. Check if virtual environment is activated")
        print("   3. Try: python manage.py runserver 0.0.0.0:8000")

if __name__ == "__main__":
    start_server()

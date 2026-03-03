#!/usr/bin/env python3
"""
PNP System LAN Setup Script
Helps configure and run the PNP system for LAN access
"""

import socket
import subprocess
import platform
import os

def get_local_ip():
    """Get the local IP address for LAN access"""
    try:
        # Connect to an external server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_system_info():
    """Get system information"""
    system = platform.system()
    return system.lower()

def create_lan_url(ip, port=8000):
    """Create LAN access URL"""
    return f"http://{ip}:{port}"

def setup_firewall_windows(port=8000):
    """Setup Windows firewall rule"""
    try:
        cmd = f'netsh advfirewall firewall add rule name="PNP Inventory System" dir=in action=allow protocol=TCP localport={port}'
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Windows firewall rule added for port {port}")
        return True
    except subprocess.CalledProcessError:
        print(f"⚠️  Could not add firewall rule (may need admin rights)")
        return False

def setup_firewall_linux(port=8000):
    """Setup Linux firewall rule"""
    try:
        # Try ufw first
        subprocess.run(['sudo', 'ufw', 'allow', f'{port}/tcp'], check=True)
        print(f"✅ UFW rule added for port {port}")
        return True
    except:
        try:
            # Try iptables
            subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', str(port), '-j', 'ACCEPT'], check=True)
            print(f"✅ iptables rule added for port {port}")
            return True
        except:
            print(f"⚠️  Could not add firewall rule (may need sudo)")
            return False

def main():
    print("PNP Inventory System - LAN Setup")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"📡 Local IP Address: {local_ip}")
    
    # Get system info
    system = get_system_info()
    print(f"💻 Operating System: {system}")
    
    # Create LAN URL
    lan_url = create_lan_url(local_ip)
    print(f"🔗 LAN Access URL: {lan_url}")
    
    # Setup firewall
    print("\n🔥 Configuring firewall...")
    if system == 'windows':
        setup_firewall_windows()
    else:
        setup_firewall_linux()
    
    # Instructions
    print("\n📋 LAN Setup Instructions:")
    print("1. Start the PNP server:")
    print("   python manage.py runserver 0.0.0.0:8000")
    print(f"\n2. Access from other devices:")
    print(f"   {lan_url}")
    print(f"\n3. Test with different devices:")
    print("   - Mobile phones")
    print("   - Tablets") 
    print("   - Other computers")
    print("   - Laptops")
    
    print("\n🧪 Testing Scenarios:")
    print("1. Login attempts from different IPs")
    print("2. Test automatic IP blocking")
    print("3. Test domain blocking")
    print("4. Test agent functionality")
    print("5. Test security incidents")
    
    print("\n🔒 Security Notes:")
    print("- All login attempts will be tracked")
    print("- IPs will be blocked after 10 failed attempts")
    print("- Domain blocking works for all devices")
    print("- Security incidents can be created from any device")
    
    print(f"\n🎯 Ready! Other devices can now connect to:")
    print(f"   {lan_url}")

if __name__ == "__main__":
    main()

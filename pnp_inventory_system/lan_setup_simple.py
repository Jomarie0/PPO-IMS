import socket

def get_local_ip():
    """Get the local IP address for LAN access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def main():
    print("PNP Inventory System - LAN Setup")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"Local IP Address: {local_ip}")
    
    # Create LAN URL
    lan_url = f"http://{local_ip}:8000"
    print(f"LAN Access URL: {lan_url}")
    
    print("\nSetup Instructions:")
    print("1. Start server: python manage.py runserver 0.0.0.0:8000")
    print(f"2. Access from other devices: {lan_url}")
    print("3. Test with phones, tablets, other computers")
    
    print("\nTesting Scenarios:")
    print("- Login attempts from different IPs")
    print("- Test automatic IP blocking (10 failed attempts)")
    print("- Test domain blocking")
    print("- Test security incidents")
    print("- Test agent functionality")
    
    print(f"\nReady! Other devices can connect to: {lan_url}")

if __name__ == "__main__":
    main()

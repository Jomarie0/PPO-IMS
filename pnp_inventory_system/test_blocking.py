"""
Simple test script to verify blocking functionality
Run this in Django shell: python manage.py shell
"""

from cybersecurity.models import BlockedIP, BlockedDomain, LoginAttempt
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def test_ip_blocking():
    """Test IP blocking functionality"""
    print("=== Testing IP Blocking ===")
    
    # Create a test IP block
    test_ip = "192.168.1.999"
    blocked_ip = BlockedIP.objects.create(
        ip_address=test_ip,
        reason="Test block",
        is_active=True
    )
    print(f"✅ Created blocked IP: {test_ip}")
    
    # Test client
    client = Client()
    
    # Try to access with blocked IP
    response = client.get('/', REMOTE_ADDR=test_ip)
    print(f"✅ Response status: {response.status_code}")
    
    if response.status_code == 403:
        print("✅ IP Blocking WORKS - Got 403 Forbidden")
    else:
        print("❌ IP Blocking FAILED - Expected 403, got", response.status_code)
    
    # Clean up
    blocked_ip.delete()
    print("✅ Test completed")

def test_auto_blocking():
    """Test automatic IP blocking after failed attempts"""
    print("\n=== Testing Auto Blocking ===")
    
    test_ip = "192.168.1.888"
    
    # Create 5 failed login attempts
    for i in range(5):
        LoginAttempt.objects.create(
            ip_address=test_ip,
            success=False,
            user_agent="Test Agent",
            username_attempted=f"testuser{i}",
            timestamp=timezone.now() - timedelta(minutes=i)
        )
    
    print(f"✅ Created 5 failed login attempts for {test_ip}")
    
    # Check if IP was auto-blocked
    is_blocked = BlockedIP.objects.filter(ip_address=test_ip, is_active=True).exists()
    
    if is_blocked:
        print("✅ Auto Blocking WORKS - IP was automatically blocked")
    else:
        print("❌ Auto Blocking FAILED - IP was not blocked")
    
    # Clean up
    LoginAttempt.objects.filter(ip_address=test_ip).delete()
    BlockedIP.objects.filter(ip_address=test_ip).delete()
    print("✅ Test completed")

def test_toggle_functionality():
    """Test toggle block status functionality"""
    print("\n=== Testing Toggle Functionality ===")
    
    # Create test block
    test_ip = "192.168.1.777"
    blocked_ip = BlockedIP.objects.create(
        ip_address=test_ip,
        reason="Test toggle",
        is_active=True
    )
    
    print(f"✅ Created active block for {test_ip}")
    
    # Toggle status
    blocked_ip.is_active = not blocked_ip.is_active
    blocked_ip.save()
    
    print(f"✅ Toggled status - Now: {'Active' if blocked_ip.is_active else 'Inactive'}")
    
    # Clean up
    blocked_ip.delete()
    print("✅ Test completed")

if __name__ == "__main__":
    print("🧪 Testing PNP Security Blocking Features")
    print("=" * 50)
    
    test_ip_blocking()
    test_auto_blocking()
    test_toggle_functionality()
    
    print("\n🎉 All tests completed!")

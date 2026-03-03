import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from cybersecurity.models import BlockedIP, WhitelistedIP, LoginAttempt
from django.utils import timezone

def debug_autoblock():
    """Debug why auto-block isn't triggering"""
    print("Debugging auto-block behavior...")
    
    # Create test user
    User = get_user_model()
    test_user = User.objects.filter(is_superuser=True).first()
    
    if not test_user:
        test_user = User.objects.create_user(
            username='debuguser',
            email='debug@example.com',
            password='debugpass123'
        )
    
    client = Client()
    client.force_login(test_user)
    
    # Test IP
    test_ip = "192.168.1.777"
    
    print(f"Testing IP: {test_ip}")
    
    # Clear any existing attempts
    LoginAttempt.objects.filter(ip_address=test_ip).delete()
    BlockedIP.objects.filter(ip_address=test_ip).delete()
    
    # Simulate 10 failed attempts within 1 hour
    print("Creating 10 failed attempts within 1 hour...")
    now = timezone.now()
    for i in range(10):
        LoginAttempt.objects.create(
            user=None,
            ip_address=test_ip,
            success=False,
            user_agent="Debug Test",
            username_attempted=f"debuguser{i}",
            timestamp=now - timezone.timedelta(minutes=59-i)  # All within last hour
        )
    
    # Check failed count
    failed_count = LoginAttempt.objects.filter(
        ip_address=test_ip,
        success=False,
        timestamp__gte=now - timezone.timedelta(hours=1)
    ).count()
    
    print(f"Failed attempts in last hour: {failed_count}")
    
    # Manually trigger the auto-block logic
    from cybersecurity.middleware import SecurityMiddleware
    
    # Create a mock request
    class MockRequest:
        def __init__(self, ip):
            self.META = {'REMOTE_ADDR': ip}
            self.ip_address = ip
    
    class MockResponse:
        def __init__(self):
            pass
    
    # Mock the get_response method
    def mock_get_response(request):
        return MockResponse()
    
    # Create middleware instance with mocked get_response
    middleware = SecurityMiddleware(get_response=mock_get_response)
    
    # Create a mock request
    mock_request = MockRequest(test_ip)
    
    # Call the auto-block function
    middleware.check_and_block_ip(test_ip)
    
    # Check if block was created
    is_blocked = BlockedIP.objects.filter(ip_address=test_ip, is_active=True).exists()
    
    if is_blocked:
        block = BlockedIP.objects.get(ip_address=test_ip, is_active=True)
        print(f"SUCCESS: Auto-block triggered!")
        print(f"  IP: {block.ip_address}")
        print(f"  Reason: {block.reason}")
        print(f"  Time: {block.date_blocked}")
    else:
        print("FAILED: Auto-block did not trigger")
        print(f"  Failed count: {failed_count}")
        print(f"  Threshold: 10")
    
    # Test the middleware process_request method
    print("\nTesting middleware process_request...")
    response = middleware.process_request(mock_request)
    
    if response:
        print(f"Middleware returned 403: {response}")
    else:
        print("Middleware allowed request")

if __name__ == "__main__":
    debug_autoblock()

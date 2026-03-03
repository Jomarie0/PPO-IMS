import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from cybersecurity.models import BlockedIP, LoginAttempt
from django.utils import timezone

def test_blocking_fix():
    """Test that blocking works without duplicate errors"""
    print("Testing blocking fix...")
    
    # Create test user
    User = get_user_model()
    test_user = User.objects.filter(is_superuser=True).first()
    
    if not test_user:
        test_user = User.objects.create_user(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )
    
    client = Client()
    client.force_login(test_user)
    
    # Test IP
    test_ip = "192.168.1.999"
    
    print(f"Testing IP: {test_ip}")
    
    # Clear any existing attempts and blocks
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
            user_agent="Test Browser",
            username_attempted=f"testuser{i}",
            timestamp=now - timezone.timedelta(minutes=59-i)  # All within last hour
        )
    
    # Test the auto-blocking logic
    from cybersecurity.middleware import SecurityMiddleware
    from django.http import HttpResponse
    
    # Mock the get_response method
    def mock_get_response(request):
        return HttpResponse("OK")
    
    # Create middleware instance
    middleware = SecurityMiddleware(get_response=mock_get_response)
    
    # Call the auto-block function
    print("Triggering auto-block...")
    middleware.check_and_block_ip(test_ip)
    
    # Check if block was created
    is_blocked = BlockedIP.objects.filter(ip_address=test_ip, is_active=True).exists()
    
    if is_blocked:
        block = BlockedIP.objects.get(ip_address=test_ip, is_active=True)
        print("SUCCESS: Auto-block triggered!")
        print(f"  IP: {block.ip_address}")
        print(f"  Reason: {block.reason}")
        print(f"  Time: {block.date_blocked}")
        
        # Test that calling it again doesn't create duplicates
        print("\nTesting duplicate prevention...")
        middleware.check_and_block_ip(test_ip)
        
        # Should still only have one record
        block_count = BlockedIP.objects.filter(ip_address=test_ip).count()
        print(f"Total blocked records for {test_ip}: {block_count}")
        
        if block_count == 1:
            print("SUCCESS: No duplicates created!")
        else:
            print(f"FAILED: Found {block_count} records (should be 1)")
    else:
        print("FAILED: Auto-block did not trigger")
    
    print("\nBlocking fix test completed!")

if __name__ == "__main__":
    test_blocking_fix()

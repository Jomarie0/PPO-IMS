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

def test_wrong_password_behavior():
    """Test what happens with wrong passwords"""
    print("Testing wrong password behavior...")
    
    # Create test user
    User = get_user_model()
    test_user = User.objects.filter(is_superuser=True).first()
    
    if not test_user:
        print("No superuser found. Creating test user...")
        test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    client = Client()
    client.force_login(test_user)
    
    # Test IP
    test_ip = "192.168.1.999"
    
    print(f"\nTesting with IP: {test_ip}")
    print("Current threshold: 10 failed attempts")
    
    # Simulate 9 failed attempts
    print("\nSimulating 9 failed login attempts...")
    for i in range(9):
        LoginAttempt.objects.create(
            user=None,
            ip_address=test_ip,
            success=False,
            user_agent="Test Browser",
            username_attempted=f"testuser{i}",
            timestamp=timezone.now() - timezone.timedelta(minutes=i)
        )
        print(f"  Failed attempt {i+1} created")
    
    # Check if IP is blocked yet
    is_blocked = BlockedIP.objects.filter(ip_address=test_ip, is_active=True).exists()
    print(f"IP currently blocked: {is_blocked}")
    
    # Test 10th attempt (should trigger auto-block)
    print("\nTesting 10th failed login attempt...")
    
    # Try to access a protected page
    response = client.get('/cybersecurity/blocklist/', REMOTE_ADDR=test_ip)
    
    if response.status_code == 403:
        print("SUCCESS: 10th attempt triggered auto-block (403 Forbidden)")
    else:
        print(f"UNEXPECTED: Got status {response.status_code} instead of 403")
    
    # Check if block was created
    block_created = BlockedIP.objects.filter(ip_address=test_ip, is_active=True).exists()
    print(f"Block created in database: {block_created}")
    
    if block_created:
        block = BlockedIP.objects.get(ip_address=test_ip, is_active=True)
        print(f"Block details: {block.reason} at {block.date_blocked}")
    
    # Test with whitelisted IP
    print("\nTesting with whitelisted IP...")
    whitelisted_ip = "192.168.1.888"
    
    # Add to whitelist
    WhitelistedIP.objects.create(
        ip_address=whitelisted_ip,
        reason="Test whitelist IP",
        added_by=None
    )
    print(f"Added {whitelisted_ip} to whitelist")
    
    # Simulate 20 failed attempts on whitelisted IP
    print("Simulating 20 failed attempts on whitelisted IP...")
    for i in range(20):
        LoginAttempt.objects.create(
            user=None,
            ip_address=whitelisted_ip,
            success=False,
            user_agent="Test Browser",
            username_attempted=f"testuser{i}",
            timestamp=timezone.now() - timezone.timedelta(minutes=i)
        )
    
    # Test access with whitelisted IP
    response = client.get('/cybersecurity/blocklist/', REMOTE_ADDR=whitelisted_ip)
    
    if response.status_code == 200:
        print("SUCCESS: Whitelisted IP bypasses blocking (200 OK)")
    else:
        print(f"UNEXPECTED: Whitelisted IP got {response.status_code}")
    
    print("\nWrong password behavior test completed!")

if __name__ == "__main__":
    test_wrong_password_behavior()

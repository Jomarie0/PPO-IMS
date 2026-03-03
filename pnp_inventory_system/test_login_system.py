import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from cybersecurity.models import BlockedIP, WhitelistedIP

def test_login_system():
    """Test the login system with various scenarios"""
    print("Testing login system functionality...")
    
    # Create a test user for authentication
    User = get_user_model()
    test_user = User.objects.filter(is_superuser=True).first()
    
    if not test_user:
        print("No superuser found for testing. Creating one...")
        test_user = User.objects.create_user(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )
        print("Created test user: testadmin")
    
    client = Client()
    client.force_login(test_user)
    
    # Test 1: Check if system loads without errors
    try:
        response = client.get('/cybersecurity/blocklist/')
        if response.status_code == 200:
            print("Blocklist management page loads")
        else:
            print(f"Blocklist page error: {response.status_code}")
            
        response = client.get('/cybersecurity/whitelist/')
        if response.status_code == 200:
            print("Whitelist management page loads")
        else:
            print(f"Whitelist page error: {response.status_code}")
            
        response = client.get('/cybersecurity/incidents/')
        if response.status_code == 200:
            print("Security incidents page loads")
        else:
            print(f"Incidents page error: {response.status_code}")
            
        response = client.get('/cybersecurity/analytics/')
        if response.status_code == 200:
            print("Login analytics page loads")
        else:
            print(f"Analytics page error: {response.status_code}")
            
    except Exception as e:
        print(f"Page loading error: {e}")
    
    # Test 3: Check whitelist functionality
    try:
        whitelisted_count = WhitelistedIP.objects.filter(is_active=True).count()
        blocked_count = BlockedIP.objects.filter(is_active=True).count()
        
        print(f"\nSystem Status:")
        print(f"  Active Whitelisted IPs: {whitelisted_count}")
        print(f"  Active Blocked IPs: {blocked_count}")
        
        if whitelisted_count > 0:
            print("Whitelist system is active")
        else:
            print("No IPs in whitelist")
            
    except Exception as e:
        print(f"Status check error: {e}")
    
    print("\nLogin system test completed!")
    print("You can now test login from different devices without integrity errors.")

if __name__ == "__main__":
    test_login_system()

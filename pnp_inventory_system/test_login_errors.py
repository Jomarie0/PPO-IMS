import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from users.models import CustomUser

def test_login_error_handling():
    """Test that login errors are properly displayed"""
    print("Testing login error handling...")
    
    # Create test user
    User = get_user_model()
    test_user = User.objects.filter(username='testadmin').first()
    
    if not test_user:
        print("Creating test user...")
        test_user = User.objects.create_user(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )
    
    client = Client()
    
    # Test 1: Wrong password
    print("\nTest 1: Wrong password")
    response = client.post('/users/login/', {
        'username': 'testadmin',
        'password': 'wrongpassword'
    })
    
    if response.status_code == 200:
        print("Wrong password: Stays on login page (correct)")
        # Check if error message is in response
        if 'Invalid password' in str(response.content):
            print("Error message displayed: 'Invalid password'")
        else:
            print("Error message not found in response")
    else:
        print(f"Wrong password: Unexpected status {response.status_code}")
    
    # Test 2: Wrong username
    print("\nTest 2: Wrong username")
    response = client.post('/users/login/', {
        'username': 'nonexistentuser',
        'password': 'anypassword'
    })
    
    if response.status_code == 200:
        print("Wrong username: Stays on login page (correct)")
        if 'Invalid username or password' in str(response.content):
            print("Error message displayed: 'Invalid username or password'")
        else:
            print("Error message not found in response")
    else:
        print(f"Wrong username: Unexpected status {response.status_code}")
    
    # Test 3: Empty fields
    print("\nTest 3: Empty fields")
    response = client.post('/users/login/', {
        'username': '',
        'password': ''
    })
    
    if response.status_code == 200:
        print("Empty fields: Stays on login page (correct)")
        if 'This field is required' in str(response.content):
            print("Validation errors displayed: 'This field is required'")
        else:
            print("Validation errors not found in response")
    else:
        print(f"Empty fields: Unexpected status {response.status_code}")
    
    # Test 4: Correct login
    print("\nTest 4: Correct login")
    response = client.post('/users/login/', {
        'username': 'testadmin',
        'password': 'testpass123'
    })
    
    if response.status_code == 302:
        print("Correct login: Redirects to dashboard (correct)")
    else:
        print(f"Correct login: Unexpected status {response.status_code}")
    
    print("\nLogin error handling test completed!")

if __name__ == "__main__":
    test_login_error_handling()

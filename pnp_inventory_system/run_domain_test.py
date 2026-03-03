#!/usr/bin/env python
"""
Direct test script for domain blocking
Run with: python run_domain_test.py
"""

import os
import sys
import django

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cybersecurity.models import BlockedDomain
from django.test import Client

def test_domain_blocking():
    """Test domain blocking functionality"""
    print("=== Testing Domain Blocking ===")
    
    # Create a test domain block
    test_domain = "https://www.y8.com/"
    blocked_domain = BlockedDomain.objects.create(
        domain=test_domain,
        reason="Test domain block",
        is_active=True
    )
    print(f"✅ Created blocked domain: {test_domain}")
    
    # Test client
    client = Client()
    
    # Try to access with blocked domain
    response = client.get('/', HTTP_HOST=test_domain)
    print(f"✅ Response status: {response.status_code}")
    
    if response.status_code == 403:
        print("✅ Domain Blocking WORKS - Got 403 Forbidden")
    else:
        print("❌ Domain Blocking FAILED - Expected 403, got", response.status_code)
    
    # Test with www prefix (remove https:// for HTTP_HOST)
    clean_domain = test_domain.replace("https://", "")
    response_www = client.get('/', HTTP_HOST=f"www.{clean_domain}")
    print(f"✅ WWW subdomain response: {response_www.status_code}")
    
    if response_www.status_code == 403:
        print("✅ WWW Domain Blocking WORKS")
    else:
        print("❌ WWW Domain Blocking FAILED")
    
    # Test with subdomain
    response_sub = client.get('/', HTTP_HOST=f"sub.{clean_domain}")
    print(f"✅ Subdomain response: {response_sub.status_code}")
    
    if response_sub.status_code == 403:
        print("✅ Subdomain Blocking WORKS")
    else:
        print("❌ Subdomain Blocking FAILED")
    
    # Clean up
    blocked_domain.delete()
    print("✅ Test completed")

if __name__ == "__main__":
    print("🌐 Testing PNP Domain Blocking Features")
    print("=" * 50)
    test_domain_blocking()
    print("\n🎉 Domain blocking test completed!")

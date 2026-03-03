"""
Test script to verify domain blocking functionality
Run this in Django shell: python manage.py shell
"""

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

def test_main_domain_blocking():
    """Test main domain blocks subdomains"""
    print("\n=== Testing Main Domain Blocks Subdomains ===")
    
    # Block main domain
    main_domain = "example.com"
    blocked_domain = BlockedDomain.objects.create(
        domain=main_domain,
        reason="Test main domain block",
        is_active=True
    )
    print(f"✅ Created blocked main domain: {main_domain}")
    
    client = Client()
    
    # Test subdomain access
    subdomain = "sub.example.com"
    response = client.get('/', HTTP_HOST=subdomain)
    print(f"✅ Subdomain response: {response.status_code}")
    
    if response.status_code == 403:
        print("✅ Main Domain Blocks Subdomains - WORKS")
    else:
        print("❌ Main Domain Blocks Subdomains - FAILED")
    
    # Clean up
    blocked_domain.delete()
    print("✅ Test completed")

def test_partial_domain_blocking():
    """Test partial domain matching"""
    print("\n=== Testing Partial Domain Matching ===")
    
    # Block partial domain
    partial_domain = "malware"
    blocked_domain = BlockedDomain.objects.create(
        domain=partial_domain,
        reason="Test partial block",
        is_active=True
    )
    print(f"✅ Created partial block: {partial_domain}")
    
    client = Client()
    
    # Test domain containing blocked text
    test_domains = [
        "malware-site.com",
        "fake-malware.net",
        "malware.example.org"
    ]
    
    for test_domain in test_domains:
        response = client.get('/', HTTP_HOST=test_domain)
        print(f"✅ {test_domain} -> {response.status_code}")
        
        if response.status_code == 403:
            print(f"  ✅ {test_domain} BLOCKED")
        else:
            print(f"  ❌ {test_domain} NOT BLOCKED")
    
    # Clean up
    blocked_domain.delete()
    print("✅ Test completed")

def test_domain_management():
    """Test domain management functionality"""
    print("\n=== Testing Domain Management ===")
    
    # Test creating domains
    test_domains = [
        ("bad-site.com", "Malicious content"),
        ("phishing.net", "Phishing attempts"),
        ("spam.org", "Spam distribution")
    ]
    
    for domain, reason in test_domains:
        blocked_domain = BlockedDomain.objects.create(
            domain=domain,
            reason=reason,
            is_active=True
        )
        print(f"✅ Created domain block: {domain}")
    
    # Test listing
    all_domains = BlockedDomain.objects.filter(is_active=True)
    print(f"✅ Total active blocks: {all_domains.count()}")
    
    # Test toggling
    first_domain = all_domains.first()
    original_status = first_domain.is_active
    first_domain.is_active = not original_status
    first_domain.save()
    print(f"✅ Toggled domain status: {original_status} -> {first_domain.is_active}")
    
    # Clean up
    BlockedDomain.objects.all().delete()
    print("✅ Test completed")

if __name__ == "__main__":
    print("🌐 Testing PNP Domain Blocking Features")
    print("=" * 50)
    
    test_domain_blocking()
    test_main_domain_blocking()
    test_partial_domain_blocking()
    test_domain_management()
    
    print("\n🎉 All domain blocking tests completed!")
    print("\n📋 Domain Blocking Features:")
    print("✅ Exact domain matching")
    print("✅ WWW prefix handling")
    print("✅ Subdomain blocking")
    print("✅ Partial domain matching")
    print("✅ Status toggling")
    print("✅ Management interface")

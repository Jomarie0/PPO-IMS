import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from cybersecurity.models import BlockedDomain
from django.test import Client

# Clean up any existing test domains
BlockedDomain.objects.filter(domain__contains='y8.com').delete()

# Test domain blocking
test_domain = "www.y8.com"
print("Testing domain: " + test_domain)

# Create block
blocked_domain = BlockedDomain.objects.create(
    domain=test_domain,
    reason="Test domain block",
    is_active=True
)
print("Created blocked domain: " + test_domain)

# Test with client
client = Client()
response = client.get('/', HTTP_HOST=test_domain)
print("Response status: " + str(response.status_code))

if response.status_code == 403:
    print("Domain Blocking WORKS - Got 403 Forbidden")
else:
    print("Domain Blocking FAILED - Expected 403, got " + str(response.status_code))

# Test subdomain
response_sub = client.get('/', HTTP_HOST="sub." + test_domain)
print("Subdomain response: " + str(response_sub.status_code))

if response_sub.status_code == 403:
    print("Subdomain Blocking WORKS")
else:
    print("Subdomain Blocking FAILED")

# Clean up
blocked_domain.delete()
print("Test completed")

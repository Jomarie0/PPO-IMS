import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from cybersecurity.models import BlockedDomain
from django.test import Client

# Test domain blocking
test_domain = "https://www.y8.com/"
print(f"Testing domain: {test_domain}")

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

# Clean up
blocked_domain.delete()
print("Test completed")

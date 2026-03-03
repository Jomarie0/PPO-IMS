import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from cybersecurity.models import BlockedIP

# Common development/local IPs to whitelist
dev_ips = [
    '127.0.0.1',      # Localhost
    '192.168.1.1',    # Common home router
    '192.168.0.1',    # Alternative home router
    '10.0.0.1',       # Office network
    '172.16.0.1',      # Another common private range
]

print("Whitelisting development IPs...")
for ip in dev_ips:
    # Unblock if currently blocked
    blocked = BlockedIP.objects.filter(ip_address=ip, is_active=True)
    if blocked.exists():
        blocked.update(is_active=False)
        print("  Unblocked: " + ip)
    else:
        print("  Already allowed: " + ip)

print("\nDevelopment IPs whitelisted!")
print("You can now test without getting blocked.")

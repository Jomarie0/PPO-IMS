import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from cybersecurity.models import WhitelistedIP

def add_test_whitelist():
    """Add test IPs to whitelist"""
    print("Adding test IPs to whitelist...")
    
    # Common development/local IPs to whitelist
    test_ips = [
        ('127.0.0.1', 'Localhost development'),
        ('192.168.1.1', 'Local network gateway'),
        ('192.168.0.1', 'Alternative local network'),
        ('10.0.0.1', 'Office network'),
        ('172.16.0.1', 'Private network range'),
    ]
    
    for ip, reason in test_ips:
        # Check if already exists
        if not WhitelistedIP.objects.filter(ip_address=ip).exists():
            whitelisted_ip = WhitelistedIP.objects.create(
                ip_address=ip,
                reason=reason,
                added_by=None  # System added
            )
            print("  Added: " + ip + " - " + reason)
        else:
            print("  Already exists: " + ip)
    
    print("\nWhitelist setup complete!")
    print("These IPs will never be blocked by the security system.")

if __name__ == "__main__":
    add_test_whitelist()

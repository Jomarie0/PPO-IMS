import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from cybersecurity.models import BlockedIP

# Get your current IP (you'll need to know what it is)
# Common local IPs to check
common_ips = ['127.0.0.1', '192.168.1.1', '192.168.0.1', '10.0.0.1']

print("Checking for blocked IPs...")
blocked_ips = BlockedIP.objects.filter(is_active=True)

if blocked_ips.exists():
    print("Found blocked IPs:")
    for ip in blocked_ips:
        print(f"  - {ip.ip_address} (Reason: {ip.reason[:50]}...)")
    
    # Unblock all recent automatic blocks
    auto_blocks = blocked_ips.filter(reason__contains="Automatic block")
    if auto_blocks.exists():
        print("\nUnblocking automatic blocks...")
        for block in auto_blocks:
            block.is_active = False
            block.save()
            print("  Unblocked: " + block.ip_address)
    else:
        print("\nNo automatic blocks found. Manual unblocking all...")
        for block in blocked_ips:
            block.is_active = False
            block.save()
            print("  Unblocked: " + block.ip_address)
else:
    print("No active blocks found")

print("\nDone! Try logging in again.")

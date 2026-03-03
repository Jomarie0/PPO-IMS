import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.db.models import Count
from cybersecurity.models import BlockedIP, WhitelistedIP

def test_integrity():
    """Test if integrity error is fixed"""
    print("Testing integrity after fix...")
    
    # Check for any remaining duplicates
    blocked_duplicates = BlockedIP.objects.values('ip_address').annotate(count=Count('id')).filter(count__gt=1)
    whitelist_duplicates = WhitelistedIP.objects.values('ip_address').annotate(count=Count('id')).filter(count__gt=1)
    
    if blocked_duplicates.exists():
        print("Still have duplicate blocked IPs:")
        for dup in blocked_duplicates:
            print(f"  {dup['ip_address']}: {dup['count']} duplicates")
    else:
        print("No duplicate blocked IPs found")
    
    if whitelist_duplicates.exists():
        print("Still have duplicate whitelisted IPs:")
        for dup in whitelist_duplicates:
            print(f"  {dup['ip_address']}: {dup['count']} duplicates")
    else:
        print("No duplicate whitelisted IPs found")
    
    # Show counts
    total_blocked = BlockedIP.objects.count()
    total_whitelisted = WhitelistedIP.objects.count()
    print(f"\nCurrent Status:")
    print(f"  Total Blocked IPs: {total_blocked}")
    print(f"  Total Whitelisted IPs: {total_whitelisted}")
    
    if blocked_duplicates.exists() == False and whitelist_duplicates.exists() == False:
        print("\nIntegrity error is FIXED!")
        print("You can now use the login system from all devices without integrity errors.")
    else:
        print("\nIntegrity issues still exist. Please review the data.")

if __name__ == "__main__":
    from django.db.models import Count
    test_integrity()

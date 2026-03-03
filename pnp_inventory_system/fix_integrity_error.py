import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.db.models import Count
from cybersecurity.models import BlockedIP, WhitelistedIP

def fix_integrity_error():
    """Fix integrity error by cleaning up duplicate data"""
    print("Fixing integrity error...")
    
    # Check for duplicate IPs in blocked list
    duplicates = BlockedIP.objects.values('ip_address').annotate(count=Count('id')).filter(count__gt=1)
    
    if duplicates.exists():
        print("Found duplicate blocked IPs:")
        for dup in duplicates:
            ip = dup['ip_address']
            count = dup['count']
            print(f"  {ip}: {count} duplicates")
            
            # Keep the most recent one, delete older ones
            blocked_ips = BlockedIP.objects.filter(ip_address=ip).order_by('-date_blocked')
            to_keep = blocked_ips.first()
            to_delete = blocked_ips.exclude(id=to_keep.id)
            
            print(f"  Keeping: {to_keep.date_blocked} - {to_keep.reason}")
            print(f"  Deleting {to_delete.count()} older duplicates")
            
            to_delete.delete()
    
    # Check for duplicate IPs in whitelist
    whitelist_duplicates = WhitelistedIP.objects.values('ip_address').annotate(count=Count('id')).filter(count__gt=1)
    
    if whitelist_duplicates.exists():
        print("Found duplicate whitelisted IPs:")
        for dup in whitelist_duplicates:
            ip = dup['ip_address']
            count = dup['count']
            print(f"  {ip}: {count} duplicates")
            
            # Keep the most recent one, delete older ones
            whitelisted_ips = WhitelistedIP.objects.filter(ip_address=ip).order_by('-date_added')
            to_keep = whitelisted_ips.first()
            to_delete = whitelisted_ips.exclude(id=to_keep.id)
            
            print(f"  Keeping: {to_keep.date_added} - {to_keep.reason}")
            print(f"  Deleting {to_delete.count()} older duplicates")
            
            to_delete.delete()
    
    print("\nIntegrity error fix completed!")
    print("You can now run migrations safely.")

if __name__ == "__main__":
    from django.db.models import Count
    fix_integrity_error()

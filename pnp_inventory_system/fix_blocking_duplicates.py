import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.db.models import Count
from cybersecurity.models import BlockedIP

def fix_blocking_duplicates():
    """Fix duplicate IP blocking entries"""
    print("Fixing blocking IP duplicates...")
    
    # Find all duplicate IPs
    duplicates = BlockedIP.objects.values('ip_address').annotate(count=Count('id')).filter(count__gt=1)
    
    if duplicates.exists():
        print(f"Found {duplicates.count()} duplicate IPs:")
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
    
    print("\nDuplicate blocking entries cleaned up!")
    print("Auto-blocking should work correctly now.")

if __name__ == "__main__":
    fix_blocking_duplicates()

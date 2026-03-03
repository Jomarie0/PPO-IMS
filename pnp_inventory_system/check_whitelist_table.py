import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.db import connection

def check_whitelist_table():
    """Check if whitelist table exists in database"""
    print("Checking whitelist table existence...")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(f"  {table[0]}")
        
        # Check if whitelist table exists
        whitelist_exists = any('whitelistedip' in str(table) for table in tables)
        
        if whitelist_exists:
            print("\nWhitelistedIP table exists in database!")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(cybersecurity_whitelistedip);")
            columns = cursor.fetchall()
            
            print("\nTable structure:")
            for col in columns:
                print(f"  {col[1]}: {col[2]}")
        else:
            print("\n❌ WhitelistedIP table does NOT exist in database!")
    
    print("\nCheck completed.")

if __name__ == "__main__":
    check_whitelist_table()

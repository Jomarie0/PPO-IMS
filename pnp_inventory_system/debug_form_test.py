#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from assets.models import Asset
from assets.forms import AssetForm

def test_form():
    client = Client()
    
    # Test as branch admin - create a proper user object
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Get a real user from database
    try:
        user = User.objects.get(username='lucena_admin')
        print(f'Found user in database: {user}')
        print(f'User role: {user.role}')
    except Exception as e:
        print(f'Error getting user: {e}')
        return
    
    if not user:
        print('ERROR: Could not find user in database')
        return
    
    # Get an existing asset
    asset = Asset.objects.filter(branch__code='LUCENA').first()
    if asset:
        print(f'Testing update for asset: {asset.property_number}')
        
        # Create form instance manually to test
        form = AssetForm(user=user, is_update=True)
        
        # Test form validation
        print(f'Form branch field required: {form.fields["branch"].required}')
        print(f'Form is_update flag: {getattr(form, "is_update", "NOT_SET")}')
        print(f'Form user role: {form.user.role}')
        
        # Test form submission
        form_data = {
            'property_number': 'LUCENA-2024-FINAL-TEST',
            'asset_type': 'laptop',
            'brand': 'Final Test Brand',
            'model': 'Final Test Model',
            'serial_number': 'FINAL123',
            'status': 'active',
            'date_acquired': '2024-01-01',
            'assigned_personnel': 'Final Test User',
            'remarks': 'Final test update'
        }

        response = client.post(f'/assets/{asset.pk}/update/', data=form_data)
        print(f'Asset update status: {response.status_code}')
        
        if response.status_code == 302:
            print('SUCCESS: Asset updated successfully!')
        elif response.status_code == 200:
            print('Form validation errors')
            content = response.content.decode('utf-8')
            if 'This field is required' in content and 'branch' in content.lower():
                print('ERROR: Branch field still showing as required')
            else:
                print('SUCCESS: No branch field errors!')
        else:
            print(f'Unexpected status: {response.status_code}')

if __name__ == '__main__':
    test_form()

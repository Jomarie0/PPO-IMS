from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from branches.models import Branch
from assets.models import Asset
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed initial data for PNP Inventory Management System'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating seed data...')
        
        # Create branches
        branches_data = [
            {
                'name': 'Lucena City Police Station',
                'code': 'LUCENA',
                'address': 'Quezon Avenue, Lucena City, Quezon',
                'contact_number': '(042) 373-1234',
                'email': 'lucena@pnpquezon.gov.ph',
                'municipality': 'Lucena City'
            },
            {
                'name': 'Tayabas City Police Station',
                'code': 'TAYABAS',
                'address': 'Rizal Street, Tayabas City, Quezon',
                'contact_number': '(042) 793-5678',
                'email': 'tayabas@pnpquezon.gov.ph',
                'municipality': 'Tayabas City'
            },
            {
                'name': 'Sariaya Police Station',
                'code': 'SARIAYA',
                'address': 'General Luna Street, Sariaya, Quezon',
                'contact_number': '(042) 514-9012',
                'email': 'sariaya@pnpquezon.gov.ph',
                'municipality': 'Sariaya'
            }
        ]
        
        created_branches = []
        for branch_data in branches_data:
            branch, created = Branch.objects.get_or_create(
                code=branch_data['code'],
                defaults=branch_data
            )
            if created:
                self.stdout.write(f'Created branch: {branch.name}')
            created_branches.append(branch)
        
        # Create users
        users_data = [
            {
                'username': 'super_admin',
                'email': 'superadmin@pnpquezon.gov.ph',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'super_admin',
                'password': 'super123',
                'phone_number': '09123456788'
            },
            {
                'username': 'provincial_admin',
                'email': 'admin@pnpquezon.gov.ph',
                'first_name': 'Juan',
                'last_name': 'Dela Cruz',
                'role': 'provincial_admin',
                'password': 'admin123',
                'phone_number': '09123456789'
            },
            {
                'username': 'main_lucena_admin',
                'email': 'mainlucena@pnpquezon.gov.ph',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'role': 'main_branch_admin',
                'branch': created_branches[0],
                'password': 'mainlucena123',
                'phone_number': '09123456790'
            },
            {
                'username': 'lucena_admin',
                'email': 'lucena_admin@pnpquezon.gov.ph',
                'first_name': 'Jose',
                'last_name': 'Reyes',
                'role': 'branch_admin',
                'branch': created_branches[0],
                'password': 'lucena123',
                'phone_number': '09123456791'
            },
            {
                'username': 'tayabas_admin',
                'email': 'tayabas_admin@pnpquezon.gov.ph',
                'first_name': 'Ana',
                'last_name': 'Garcia',
                'role': 'branch_admin',
                'branch': created_branches[1],
                'password': 'tayabas123',
                'phone_number': '09123456792'
            },
            {
                'username': 'sariaya_viewer',
                'email': 'sariaya_viewer@pnpquezon.gov.ph',
                'first_name': 'Pedro',
                'last_name': 'Lopez',
                'role': 'viewer',
                'branch': created_branches[2],
                'password': 'sariaya123',
                'phone_number': '09123456793'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'branch': user_data.get('branch'),
                    'phone_number': user_data['phone_number'],
                    'is_active': True
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user.username} ({user.get_role_display()})')
            created_users.append(user)
        
        # Create sample assets
        assets_data = []
        asset_types = ['desktop', 'laptop', 'printer', 'scanner', 'router']
        brands = ['Dell', 'HP', 'Lenovo', 'Canon', 'Epson', 'Cisco']
        statuses = ['active', 'active', 'under_repair', 'missing', 'active']
        
        for i, branch in enumerate(created_branches):
            for j in range(5):  # 5 assets per branch
                asset_data = {
                    'property_number': f'{branch.code}-2024-{j+1:03d}',
                    'asset_type': asset_types[j % len(asset_types)],
                    'brand': brands[j % len(brands)],
                    'model': f'Model-{j+1}',
                    'serial_number': f'SN{branch.code}{j+1:04d}',
                    'processor': 'Intel Core i5' if j % 2 == 0 else 'Intel Core i7',
                    'ram': '8GB DDR4' if j % 2 == 0 else '16GB DDR4',
                    'storage': '512GB SSD' if j % 2 == 0 else '1TB HDD',
                    'status': statuses[j % len(statuses)],
                    'date_acquired': date.today() - timedelta(days=j*30),
                    'warranty_expiration': date.today() + timedelta(days=365-j*30),
                    'assigned_personnel': f'Officer {chr(65+j)}',
                    'branch': branch,
                    'remarks': f'Sample asset {j+1} for {branch.name}'
                }
                assets_data.append(asset_data)
        
        created_assets = []
        for asset_data in assets_data:
            asset, created = Asset.objects.get_or_create(
                property_number=asset_data['property_number'],
                defaults=asset_data
            )
            if created:
                self.stdout.write(f'Created asset: {asset.property_number}')
            created_assets.append(asset)
        
        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('Super Admin: super_admin / super123')
        self.stdout.write('Provincial Admin: provincial_admin / admin123')
        self.stdout.write('Main Lucena Admin: main_lucena_admin / mainlucena123')
        self.stdout.write('Lucena Admin: lucena_admin / lucena123')
        self.stdout.write('Tayabas Admin: tayabas_admin / tayabas123')
        self.stdout.write('Sariaya Viewer: sariaya_viewer / sariaya123')
        
        self.stdout.write('\nDjango Groups Created:')
        self.stdout.write('- Super Admins')
        self.stdout.write('- Provincial Admins')
        self.stdout.write('- Main Branch Admins')
        self.stdout.write('- Branch Admins')
        self.stdout.write('- Viewers')

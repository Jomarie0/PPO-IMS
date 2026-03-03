from django.core.management.base import BaseCommand
from django.utils import timezone
from cybersecurity.models import BranchAgentToken
from branches.models import Branch


class Command(BaseCommand):
    help = 'Generate agent tokens for all active branches'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--branch',
            type=str,
            help='Generate token for specific branch (by branch code)'
        )
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Regenerate existing tokens'
        )
    
    def handle(self, *args, **options):
        branch_code = options.get('branch')
        regenerate = options.get('regenerate', False)
        
        if branch_code:
            # Generate token for specific branch
            try:
                branch = Branch.objects.get(code=branch_code.upper(), is_active=True)
                self.generate_or_update_token(branch, regenerate)
                self.stdout.write(
                    self.style.SUCCESS(f'Token generated for branch: {branch.name}')
                )
            except Branch.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Branch with code "{branch_code}" not found or inactive')
                )
        else:
            # Generate tokens for all active branches
            branches = Branch.objects.filter(is_active=True)
            count = 0
            
            for branch in branches:
                self.generate_or_update_token(branch, regenerate)
                count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully generated tokens for {count} branches')
            )
    
    def generate_or_update_token(self, branch, regenerate=False):
        """Generate or update token for a branch"""
        token, created = BranchAgentToken.objects.get_or_create(
            branch=branch,
            defaults={'is_active': True}
        )
        
        if regenerate or not created:
            # Generate new token
            token.save()  # This will generate a new UUID
            
        self.stdout.write(f'  Branch: {branch.name} | Token: {token.token}')

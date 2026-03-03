from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with enhanced RBAC using Django Groups
    """
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('provincial_admin', 'Provincial Admin'),
        ('main_branch_admin', 'Main Branch Admin'),
        ('branch_admin', 'Branch Admin'),
        ('viewer', 'Viewer'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='viewer',
        help_text="User role in the system"
    )
    branch = models.ForeignKey(
        'branches.Branch', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Assigned branch (not applicable for Super/Provincial Admin)"
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Contact phone number"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically assign user to appropriate Django Group
        """
        super().save(*args, **kwargs)
        self.assign_to_group()
    
    def assign_to_group(self):
        """
        Automatically assign user to the appropriate Django Group based on role
        """
        # Remove user from all role groups first
        role_groups = Group.objects.filter(name__in=[
            'Super Admins', 'Provincial Admins', 'Main Branch Admins', 
            'Branch Admins', 'Viewers'
        ])
        for group in role_groups:
            self.groups.remove(group)
        
        # Add user to appropriate group
        group_mapping = {
            'super_admin': 'Super Admins',
            'provincial_admin': 'Provincial Admins',
            'main_branch_admin': 'Main Branch Admins',
            'branch_admin': 'Branch Admins',
            'viewer': 'Viewers'
        }
        
        group_name = group_mapping.get(self.role)
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.add(group)
    
    @property
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    @property
    def is_provincial_admin(self):
        return self.role == 'provincial_admin'
    
    @property
    def is_main_branch_admin(self):
        return self.role == 'main_branch_admin'
    
    @property
    def is_branch_admin(self):
        return self.role == 'branch_admin'
    
    @property
    def is_viewer(self):
        return self.role == 'viewer'
    
    @property
    def can_manage_all_branches(self):
        """Check if user can manage all branches"""
        return self.role in ['super_admin', 'provincial_admin']
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['super_admin', 'provincial_admin']
    
    @property
    def can_create_assets(self):
        """Check if user can create assets"""
        return self.role in ['super_admin', 'provincial_admin', 'main_branch_admin', 'branch_admin']
    
    @property
    def can_edit_assets(self):
        """Check if user can edit assets"""
        return self.role in ['super_admin', 'provincial_admin', 'main_branch_admin', 'branch_admin']
    
    @property
    def can_delete_assets(self):
        """Check if user can delete assets"""
        return self.role in ['super_admin', 'provincial_admin']
    
    @property
    def can_view_all_assets(self):
        """Check if user can view assets from all branches"""
        return self.role in ['super_admin', 'provincial_admin']
    
    def get_accessible_branches(self):
        """Get branches this user can access"""
        if self.can_view_all_assets:
            from branches.models import Branch
            return Branch.objects.filter(is_active=True)
        elif self.branch:
            return Branch.objects.filter(id=self.branch.id)
        else:
            return Branch.objects.none()

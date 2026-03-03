from django.db import models

class Branch(models.Model):
    """
    Model representing PNP municipal branches in Quezon Province
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Full name of the municipal branch"
    )
    code = models.CharField(
        max_length=10, 
        unique=True,
        help_text="Short code for the branch"
    )
    address = models.TextField(
        help_text="Complete address of the branch"
    )
    contact_number = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Branch contact number"
    )
    email = models.EmailField(
        blank=True,
        help_text="Branch email address"
    )
    municipality = models.CharField(
        max_length=100,
        help_text="Municipality name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the branch is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        ordering = ['municipality', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def asset_count(self):
        """Return total number of assets for this branch"""
        return self.asset_set.count()
    
    @property
    def active_assets(self):
        """Return number of active assets"""
        return self.asset_set.filter(status='active').count()
    
    @property
    def under_repair_assets(self):
        """Return number of assets under repair"""
        return self.asset_set.filter(status='under_repair').count()
    
    @property
    def missing_assets(self):
        """Return number of missing assets"""
        return self.asset_set.filter(status='missing').count()
    
    @property
    def condemned_assets(self):
        """Return number of condemned assets"""
        return self.asset_set.filter(status='condemned').count()

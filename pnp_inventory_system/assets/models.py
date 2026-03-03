from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Asset(models.Model):
    """
    Model representing computer assets in PNP branches
    """
    ASSET_TYPE_CHOICES = [
        ('desktop', 'Desktop Computer'),
        ('laptop', 'Laptop Computer'),
        ('printer', 'Printer'),
        ('scanner', 'Scanner'),
        ('router', 'Router'),
        ('switch', 'Network Switch'),
        ('server', 'Server'),
        ('monitor', 'Monitor'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('under_repair', 'Under Repair'),
        ('missing', 'Missing'),
        ('condemned', 'Condemned'),
    ]
    
    property_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique property number for the asset"
    )
    asset_type = models.CharField(
        max_length=20, 
        choices=ASSET_TYPE_CHOICES,
        help_text="Type of asset"
    )
    brand = models.CharField(
        max_length=100,
        help_text="Brand/Manufacturer"
    )
    model = models.CharField(
        max_length=100,
        help_text="Model number/name"
    )
    serial_number = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Serial number of the asset"
    )
    processor = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Processor type (for computers)"
    )
    ram = models.CharField(
        max_length=50, 
        blank=True,
        help_text="RAM size (e.g., 8GB DDR4)"
    )
    storage = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Storage type and capacity (e.g., 512GB SSD)"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        help_text="Current status of the asset"
    )
    date_acquired = models.DateField(
        help_text="Date when the asset was acquired"
    )
    warranty_expiration = models.DateField(
        null=True, 
        blank=True,
        help_text="Warranty expiration date"
    )
    assigned_personnel = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Personnel assigned to this asset"
    )
    branch = models.ForeignKey(
        'branches.Branch', 
        on_delete=models.CASCADE,
        help_text="Branch where the asset is located"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Additional notes or remarks"
    )
    
    # Security compliance fields
    os_version = models.CharField(
        max_length=100,
        blank=True,
        help_text="Operating system version (e.g., Windows 11 Pro, Ubuntu 22.04)"
    )
    last_patch_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last security patch/update"
    )
    antivirus_installed = models.BooleanField(
        default=False,
        help_text="Antivirus software installed"
    )
    antivirus_last_updated = models.DateField(
        null=True,
        blank=True,
        help_text="Last antivirus definition update date"
    )
    firewall_enabled = models.BooleanField(
        default=False,
        help_text="Firewall is enabled"
    )
    disk_encrypted = models.BooleanField(
        default=False,
        help_text="Disk encryption is enabled"
    )
    last_security_scan = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last security scan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_number']),
            models.Index(fields=['branch', 'status']),
            models.Index(fields=['asset_type']),
        ]
    
    def __str__(self):
        return f"{self.property_number} - {self.brand} {self.model}"
    
    @property
    def is_under_warranty(self):
        """Check if asset is still under warranty"""
        if self.warranty_expiration:
            from django.utils import timezone
            return self.warranty_expiration > timezone.now().date()
        return False
    
    @property
    def age_in_years(self):
        """Calculate age of asset in years"""
        from django.utils import timezone
        return (timezone.now().date() - self.date_acquired).days // 365
    
    @property
    def status_display_color(self):
        """Return Bootstrap color class based on status"""
        colors = {
            'active': 'success',
            'under_repair': 'warning',
            'missing': 'danger',
            'condemned': 'secondary'
        }
        return colors.get(self.status, 'primary')
    
    @property
    def compliance_score(self):
        """Calculate security compliance score (0-100)"""
        score = 0
        
        # Antivirus installed = +20 points
        if self.antivirus_installed:
            score += 20
        
        # Antivirus updated within 30 days = +20 points
        if self.antivirus_last_updated:
            from django.utils import timezone
            days_diff = (timezone.now().date() - self.antivirus_last_updated).days
            if days_diff <= 30:
                score += 20
        
        # Firewall enabled = +20 points
        if self.firewall_enabled:
            score += 20
        
        # Disk encrypted = +20 points
        if self.disk_encrypted:
            score += 20
        
        # Last patch date within 30 days = +20 points
        if self.last_patch_date:
            from django.utils import timezone
            days_diff = (timezone.now().date() - self.last_patch_date).days
            if days_diff <= 30:
                score += 20
        
        return score
    
    @property
    def risk_level(self):
        """Calculate risk level based on compliance score"""
        score = self.compliance_score
        if score >= 80:
            return 'Low'
        elif score >= 60:
            return 'Medium'
        elif score >= 40:
            return 'High'
        else:
            return 'Critical'
    
    @property
    def risk_level_color(self):
        """Return Bootstrap color class based on risk level"""
        colors = {
            'Low': 'success',
            'Medium': 'warning',
            'High': 'danger',
            'Critical': 'dark'
        }
        return colors.get(self.risk_level, 'secondary')
    
    @property
    def security_compliance_badge_class(self):
        """Return Bootstrap badge class based on compliance score"""
        score = self.compliance_score
        if score >= 80:
            return 'bg-success'
        elif score >= 60:
            return 'bg-warning'
        elif score >= 40:
            return 'bg-danger'
        else:
            return 'bg-dark'

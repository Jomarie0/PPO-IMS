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

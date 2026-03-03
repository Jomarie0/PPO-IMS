from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditLog(models.Model):
    """
    Model to track all changes to assets for auditing purposes
    """
    ACTION_CHOICES = [
        ('create', 'CREATE'),
        ('update', 'UPDATE'),
        ('delete', 'DELETE'),
        ('report', 'REPORT'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=10, 
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    asset = models.ForeignKey(
        'assets.Asset', 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="Asset that was modified"
    )
    asset_property_number = models.CharField(
        max_length=50,
        help_text="Property number (kept even if asset is deleted)"
    )
    description = models.TextField(
        help_text="Description of the changes made"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent"
    )
    
    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['asset', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.asset_property_number} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, asset, description="", ip_address=None, user_agent=""):
        """
        Create an audit log entry
        """
        return cls.objects.create(
            user=user,
            action=action,
            asset=asset,
            asset_property_number=asset.property_number if asset else "",
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )

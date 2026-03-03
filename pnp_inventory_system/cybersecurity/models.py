from django.db import models
from django.utils import timezone
from users.models import CustomUser
from branches.models import Branch
import uuid


class BlockedIP(models.Model):
    """Model for storing blocked IP addresses"""
    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="IP address to block"
    )
    reason = models.TextField(
        help_text="Reason for blocking this IP"
    )
    blocked_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blocked_ips'
    )
    date_blocked = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"
        ordering = ['-date_blocked']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason[:50]}"


class BlockedDomain(models.Model):
    """Model for storing blocked domains"""
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Domain to block"
    )
    reason = models.TextField(
        help_text="Reason for blocking this domain"
    )
    blocked_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blocked_domains'
    )
    date_blocked = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Blocked Domain"
        verbose_name_plural = "Blocked Domains"
        ordering = ['-date_blocked']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.domain} - {self.reason[:50]}"


class WhitelistedIP(models.Model):
    """Model for storing whitelisted IP addresses (never blocked)"""
    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="IP address to whitelist (never blocked)"
    )
    reason = models.TextField(
        help_text="Reason for whitelisting this IP"
    )
    added_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whitelisted_ips'
    )
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Whitelisted IP"
        verbose_name_plural = "Whitelisted IPs"
        ordering = ['-date_added']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason[:50]}"


class BranchAgentToken(models.Model):
    """Model for branch agent tokens for API authentication"""
    branch = models.OneToOneField(
        Branch,
        on_delete=models.CASCADE,
        related_name='agent_token'
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        help_text="Unique token for API authentication"
    )
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the agent synced with the server"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Branch Agent Token"
        verbose_name_plural = "Branch Agent Tokens"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.branch.name} - {str(self.token)[:8]}"
    
    def update_last_sync(self):
        """Update the last sync timestamp"""
        self.last_sync = timezone.now()
        self.save(update_fields=['last_sync'])


class LoginAttempt(models.Model):
    """Model for tracking login attempts"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts'
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address from which login was attempted"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(
        default=False,
        help_text="Whether the login attempt was successful"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string from the request"
    )
    username_attempted = models.CharField(
        max_length=150,
        blank=True,
        help_text="Username that was attempted (for failed logins)"
    )
    
    class Meta:
        verbose_name = "Login Attempt"
        verbose_name_plural = "Login Attempts"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['success']),
            models.Index(fields=['ip_address', 'success']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else self.username_attempted
        status = "Success" if self.success else "Failed"
        return f"{status} login for {user_info} from {self.ip_address}"


class SecurityIncident(models.Model):
    """Model for logging security incidents"""
    INCIDENT_TYPE_CHOICES = [
        ('malware', 'Malware'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('data_breach', 'Data Breach'),
        ('phishing', 'Phishing'),
        ('hardware_theft', 'Hardware Theft'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='security_incidents'
    )
    reported_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_incidents'
    )
    incident_type = models.CharField(
        max_length=20,
        choices=INCIDENT_TYPE_CHOICES,
        help_text="Type of security incident"
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        help_text="Severity level of the incident"
    )
    description = models.TextField(
        help_text="Detailed description of the incident"
    )
    date_reported = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_incidents'
    )
    resolution_notes = models.TextField(
        blank=True,
        help_text="Notes about how the incident was resolved"
    )
    date_resolved = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the incident was resolved"
    )
    
    class Meta:
        verbose_name = "Security Incident"
        verbose_name_plural = "Security Incidents"
        ordering = ['-date_reported']
        indexes = [
            models.Index(fields=['asset']),
            models.Index(fields=['incident_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['resolved']),
            models.Index(fields=['date_reported']),
        ]
    
    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.asset.property_number} ({self.get_severity_display()})"
    
    def resolve(self, resolved_by, resolution_notes):
        """Mark the incident as resolved"""
        self.resolved = True
        self.resolved_by = resolved_by
        self.resolution_notes = resolution_notes
        self.date_resolved = timezone.now()
        self.save()
    
    @property
    def severity_color(self):
        """Return Bootstrap color class based on severity"""
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark'
        }
        return colors.get(self.severity, 'secondary')

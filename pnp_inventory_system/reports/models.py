from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Report(models.Model):
    """
    Model to store generated reports
    """
    REPORT_TYPE_CHOICES = [
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Report title"
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        help_text="Type of report"
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        help_text="Report format"
    )
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Branch for branch-specific reports (null for provincial)"
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who generated the report"
    )
    file_path = models.CharField(
        max_length=500,
        help_text="Path to the generated report file"
    )
    date_from = models.DateField(
        help_text="Report start date"
    )
    date_to = models.DateField(
        help_text="Report end date"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'created_at']),
            models.Index(fields=['branch', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

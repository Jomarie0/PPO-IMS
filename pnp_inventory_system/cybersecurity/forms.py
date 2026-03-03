from django import forms
from .models import BlockedIP, BlockedDomain, SecurityIncident, WhitelistedIP
from assets.models import Asset


class BlockedIPForm(forms.ModelForm):
    """Form for adding blocked IPs"""
    class Meta:
        model = BlockedIP
        fields = ['ip_address', 'reason', 'is_active']
        widgets = {
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '192.168.1.1'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for blocking this IP address'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_ip_address(self):
        ip_address = self.cleaned_data.get('ip_address')
        
        # Check if IP is already blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            raise forms.ValidationError("This IP address is already in the blocklist.")
        
        return ip_address


class BlockedDomainForm(forms.ModelForm):
    """Form for adding blocked domains"""
    class Meta:
        model = BlockedDomain
        fields = ['domain', 'reason', 'is_active']
        widgets = {
            'domain': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'malicious-site.com'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for blocking this domain'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_domain(self):
        domain = self.cleaned_data.get('domain')
        
        # Clean domain format
        domain = domain.lower().strip()
        
        # Check if domain is already blocked
        if BlockedDomain.objects.filter(domain=domain).exists():
            raise forms.ValidationError("This domain is already in the blocklist.")
        
        return domain


class SecurityIncidentForm(forms.ModelForm):
    """Form for reporting security incidents"""
    class Meta:
        model = SecurityIncident
        fields = ['asset', 'incident_type', 'severity', 'description']
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-control'}),
            'incident_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the security incident...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter assets based on user role
        if self.user and self.user.can_view_all_assets:
            # Admin can see all assets
            self.fields['asset'].queryset = Asset.objects.select_related('branch').all()
        elif self.user and self.user.branch:
            # Branch users can only see their branch assets
            self.fields['asset'].queryset = Asset.objects.filter(branch=self.user.branch)
        else:
            # No assets available
            self.fields['asset'].queryset = Asset.objects.none()
        
        # Add empty choice
        self.fields['asset'].empty_label = "Select an asset..."
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 10:
            raise forms.ValidationError("Please provide a more detailed description (at least 10 characters).")
        return description


class QuickIncidentForm(forms.ModelForm):
    """Quick form for reporting incidents from asset detail page"""
    class Meta:
        model = SecurityIncident
        fields = ['incident_type', 'severity', 'description']
        widgets = {
            'incident_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the incident...'
            })
        }
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 10:
            raise forms.ValidationError("Please provide a more detailed description (at least 10 characters).")
        return description


class BranchTokenForm(forms.Form):
    """Form for generating branch agent tokens"""
    branch = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a branch..."
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from branches.models import Branch
        self.fields['branch'].queryset = Branch.objects.filter(is_active=True).order_by('name')


class WhitelistedIPForm(forms.ModelForm):
    """Form for adding whitelisted IP addresses"""
    class Meta:
        model = WhitelistedIP
        fields = ['ip_address', 'reason']
        widgets = {
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.100'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for whitelisting this IP'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ip_address'].label = 'IP Address'
        self.fields['reason'].label = 'Reason for Whitelisting'
        self.fields['reason'].required = False

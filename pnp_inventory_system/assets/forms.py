from django import forms
from .models import Asset
from branches.models import Branch

class AssetForm(forms.ModelForm):
    """
    Form for creating and updating assets
    """
    class Meta:
        model = Asset
        fields = [
            'property_number', 'asset_type', 'brand', 'model', 'serial_number',
            'processor', 'ram', 'storage', 'status', 'date_acquired', 
            'warranty_expiration', 'assigned_personnel', 'branch', 'remarks'
        ]
        widgets = {
            'property_number': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'processor': forms.TextInput(attrs={'class': 'form-control'}),
            'ram': forms.TextInput(attrs={'class': 'form-control'}),
            'storage': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date_acquired': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_personnel': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)
        
        # Filter branches based on user role
        if self.user and hasattr(self.user, 'role'):
            user_role = self.user.role
        else:
            user_role = None
        
        if user_role == 'branch_admin':
            self.fields['branch'].queryset = Branch.objects.filter(id=self.user.branch.id)
            self.fields['branch'].initial = self.user.branch
            self.fields['branch'].widget.attrs['disabled'] = True
            # Add hidden field to preserve branch value (only for creation)
            if not self.is_update:
                self.fields['branch_hidden'] = forms.CharField(
                    widget=forms.HiddenInput(),
                    initial=self.user.branch.id
                )
        elif user_role == 'viewer':
            self.fields['branch'].queryset = Branch.objects.filter(id=self.user.branch.id)
            self.fields['branch'].initial = self.user.branch
            self.fields['branch'].widget.attrs['disabled'] = True
            # Add hidden field to preserve branch value (only for creation)
            if not self.is_update:
                self.fields['branch_hidden'] = forms.CharField(
                    widget=forms.HiddenInput(),
                    initial=self.user.branch.id
                )
        else:
            self.fields['branch'].queryset = Branch.objects.filter(is_active=True)
        
        # Make branch field required
        self.fields['branch'].required = True
    
    def clean_property_number(self):
        property_number = self.cleaned_data.get('property_number')
        
        # Check if property number is unique
        queryset = Asset.objects.filter(property_number=property_number)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError("Property number must be unique.")
        
        return property_number
    
    def clean_date_acquired(self):
        date_acquired = self.cleaned_data.get('date_acquired')
        warranty_expiration = self.cleaned_data.get('warranty_expiration')
        
        if warranty_expiration and date_acquired:
            if warranty_expiration < date_acquired:
                raise forms.ValidationError("Warranty expiration must be after date acquired.")
        
        return date_acquired
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Handle branch field for disabled cases
        if self.user and self.user.role in ['branch_admin', 'viewer']:
            # For update forms, branch is already assigned to asset, no validation needed
            if self.is_update:
                if 'branch' in self._errors:
                    del self._errors['branch']
            else:
                # For creation forms, set branch from hidden field
                if 'branch_hidden' in cleaned_data:
                    cleaned_data['branch'] = Branch.objects.get(id=cleaned_data['branch_hidden'])
                    # Remove the branch field error if it exists
                    if 'branch' in self._errors:
                        del self._errors['branch']
        else:
            # For other users, use custom branch validation
            branch = self.clean_branch()
            if branch:
                cleaned_data['branch'] = branch
        
        return cleaned_data
    
    def clean_branch(self):
        branch = self.cleaned_data.get('branch')
        
        # Skip validation for branch admins and viewers (branch is pre-set)
        if self.user and self.user.role in ['branch_admin', 'viewer']:
            return branch
        
        # Normal validation for other users
        if not branch:
            raise forms.ValidationError("Branch is required.")
        
        return branch

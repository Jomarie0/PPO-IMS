from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from branches.models import Branch

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating new users with enhanced RBAC roles
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        empty_label="Select Branch (Not required for Super/Provincial Admin)"
    )
    phone_number = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 
                 'branch', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Make branch field required if role is not admin-level
        if 'role' in self.data and self.data['role'] not in ['super_admin', 'provincial_admin']:
            self.fields['branch'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        branch = cleaned_data.get('branch')
        
        if role not in ['super_admin', 'provincial_admin'] and not branch:
            raise forms.ValidationError("Branch is required for Main Branch Admin, Branch Admin, and Viewer roles.")
        
        return cleaned_data

class CustomUserUpdateForm(forms.ModelForm):
    """
    Form for updating existing users with enhanced RBAC roles
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 
                 'branch', 'phone_number', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_active':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

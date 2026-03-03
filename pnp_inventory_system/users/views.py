from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserUpdateForm

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

def role_required(*roles):
    """
    Enhanced decorator to require specific user roles using Django Groups
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse_lazy('users:login'))
            
            user_role = request.user.role
            if user_role not in roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard:home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Create a method decorator version for class-based views
def method_role_required(*roles):
    """
    Method decorator version of role_required for class-based views
    """
    return method_decorator(role_required(*roles))

class CustomLoginView(LoginView):
    """
    Custom login view with Bootstrap styling
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:home')

class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been successfully logged out.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_next_page(self):
        return reverse_lazy('users:login')

class UserCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new users (Super/Provincial Admin only)
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')
    
    @method_role_required('super_admin', 'provincial_admin')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f"User {form.cleaned_data['username']} has been created successfully.")
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating users (Super/Provincial Admin only)
    """
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')
    
    @method_role_required('super_admin', 'provincial_admin')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f"User {form.cleaned_data['username']} has been updated successfully.")
        return super().form_valid(form)

class UserListView(LoginRequiredMixin, ListView):
    """
    View for listing users (Super/Provincial Admin only)
    """
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    @method_role_required('super_admin', 'provincial_admin')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return CustomUser.objects.all().order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate statistics
        all_users = CustomUser.objects.all()
        context['total_users'] = all_users.count()
        context['active_users'] = all_users.filter(is_active=True).count()
        context['provincial_admins'] = all_users.filter(role='provincial_admin').count()
        context['branch_admins'] = all_users.filter(role='branch_admin').count()
        context['super_admins'] = all_users.filter(role='super_admin').count()
        context['main_branch_admins'] = all_users.filter(role='main_branch_admin').count()
        context['viewers'] = all_users.filter(role='viewer').count()
        
        return context

@login_required
def profile_view(request):
    """
    View for user profile
    """
    return render(request, 'users/profile.html', {'user': request.user})

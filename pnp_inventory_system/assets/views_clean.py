from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Asset
from .forms import AssetForm
from users.views import role_required
from audit_logs.models import AuditLog

class AssetCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new assets
    """
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')
    
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('users:login')
        
        # Only users with create permissions can create assets
        if not self.request.user.can_create_assets:
            messages.error(self.request, "You don't have permission to create assets.")
            return redirect('dashboard:home')
        
        return super().dispatch(*args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log the creation
        AuditLog.log_action(
            user=self.request.user,
            action='create',
            asset=self.object,
            description=f"Created new asset: {self.object.property_number}",
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, f"Asset {form.instance.property_number} has been created successfully.")
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class AssetUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating existing assets
    """
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')
    
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('users:login')
        
        asset = self.get_object()
        
        # Check permissions using enhanced RBAC
        if self.request.user.can_view_all_assets:
            return super().dispatch(*args, **kwargs)
        elif self.request.user.can_edit_assets and asset.branch == self.request.user.branch:
            return super().dispatch(*args, **kwargs)
        else:
            messages.error(self.request, "You can only edit assets from your branch.")
            return redirect('assets:asset_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Get old values for audit log
        old_asset = Asset.objects.get(pk=self.object.pk)
        changes = []
        
        for field in form.changed_data:
            old_value = getattr(old_asset, field)
            new_value = getattr(self.object, field)
            changes.append(f"{field}: {old_value} → {new_value}")
        
        response = super().form_valid(form)
        
        # Log the update
        if changes:
            AuditLog.log_action(
                user=self.request.user,
                action='update',
                asset=self.object,
                description=f"Updated asset: {', '.join(changes)}",
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class AssetListView(LoginRequiredMixin, ListView):
    """
    View for listing assets with filtering and pagination
    """
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Asset.objects.select_related('branch').all()
        
        # Filter by user role using enhanced RBAC
        if self.request.user.can_view_all_assets:
            return queryset
        elif self.request.user.branch:
            return queryset.filter(branch=self.request.user.branch)
        else:
            return Asset.objects.none()
        
        # Apply filters
        search = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')
        branch_filter = self.request.GET.get('branch')
        asset_type_filter = self.request.GET.get('asset_type')
        
        if search:
            queryset = queryset.filter(
                Q(property_number__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search) |
                Q(serial_number__icontains=search) |
                Q(assigned_personnel__icontains=search)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if branch_filter and self.request.user.can_view_all_assets:
            queryset = queryset.filter(branch_id=branch_filter)
        
        if asset_type_filter:
            queryset = queryset.filter(asset_type=asset_type_filter)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['status_choices'] = Asset.STATUS_CHOICES
        context['asset_type_choices'] = Asset.ASSET_TYPE_CHOICES
        
        # Add branches for filter (only for users who can view all branches)
        if self.request.user.can_view_all_assets:
            from branches.models import Branch
            context['branches'] = Branch.objects.filter(is_active=True)
        
        # Add current filters
        context['current_search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_branch'] = self.request.GET.get('branch', '')
        context['current_asset_type'] = self.request.GET.get('asset_type', '')
        
        return context

class AssetDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting assets
    """
    model = Asset
    template_name = 'assets/asset_confirm_delete.html'
    success_url = reverse_lazy('assets:asset_list')
    
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('users:login')
        
        asset = self.get_object()
        
        # Only users with delete permissions can delete assets
        if not self.request.user.can_delete_assets:
            messages.error(self.request, "Only Provincial Admin can delete assets.")
            return redirect('assets:asset_list')
        
        return super().dispatch(*args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        asset = self.get_object()
        
        # Log the deletion
        AuditLog.log_action(
            user=self.request.user,
            action='delete',
            asset=asset,
            description=f"Deleted asset: {asset.property_number}",
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, f"Asset {asset.property_number} has been deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

@login_required
def asset_detail_view(request, pk):
    """
    View for displaying asset details
    """
    asset = get_object_or_404(Asset, pk=pk)
    
    # Get audit logs for this asset
    audit_logs = AuditLog.objects.filter(asset=asset).order_by('-timestamp')[:10]
    
    context = {
        'asset': asset,
        'audit_logs': audit_logs
    }
    
    # Check permissions using enhanced RBAC
    if request.user.can_view_all_assets:
        return render(request, 'assets/asset_detail.html', context)
    elif request.user.branch and asset.branch == request.user.branch:
        return render(request, 'assets/asset_detail.html', context)
    else:
        messages.error(request, "You can only view assets from your branch.")
        return redirect('assets:asset_list')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
import json

from .models import BlockedIP, BlockedDomain, BranchAgentToken, LoginAttempt, SecurityIncident, WhitelistedIP
from .forms import BlockedIPForm, BlockedDomainForm, SecurityIncidentForm, WhitelistedIPForm
from users.models import CustomUser
from branches.models import Branch
from audit_logs.models import AuditLog


class BlocklistManagementView(LoginRequiredMixin, ListView):
    """Main view for managing IP and domain blocklists"""
    template_name = 'cybersecurity/blocklist_management.html'
    context_object_name = 'blocklist_items'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # Only Super Admin and Provincial Admin can access
        if not request.user.role in ['super_admin', 'provincial_admin']:
            messages.error(request, "You don't have permission to access blocklist management.")
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        # This will be overridden in get_context_data
        return BlockedIP.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get blocked IPs
        blocked_ips = BlockedIP.objects.all().order_by('-date_blocked')
        ip_paginator = Paginator(blocked_ips, 10)
        ip_page = self.request.GET.get('ip_page', 1)
        context['blocked_ips'] = ip_paginator.get_page(ip_page)
        
        # Get blocked domains
        blocked_domains = BlockedDomain.objects.all().order_by('-date_blocked')
        domain_paginator = Paginator(blocked_domains, 10)
        domain_page = self.request.GET.get('domain_page', 1)
        context['blocked_domains'] = domain_paginator.get_page(domain_page)
        
        # Get active tokens count
        context['active_tokens_count'] = BranchAgentToken.objects.filter(is_active=True).count()
        
        return context


class AddBlockedIPView(LoginRequiredMixin, CreateView):
    """View to add a new blocked IP"""
    model = BlockedIP
    form_class = BlockedIPForm
    template_name = 'cybersecurity/add_blocked_ip.html'
    success_url = reverse_lazy('cybersecurity:blocklist_management')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role in ['super_admin', 'provincial_admin']:
            messages.error(request, "You don't have permission to block IPs.")
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.blocked_by = self.request.user
        
        response = super().form_valid(form)
        
        # Log the action
        AuditLog.log_action(
            user=self.request.user,
            action='create',
            asset=None,
            description=f"Blocked IP: {form.instance.ip_address} - {form.instance.reason}",
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, f"IP {form.instance.ip_address} has been blocked successfully.")
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class AddBlockedDomainView(LoginRequiredMixin, CreateView):
    """View to add a new blocked domain"""
    model = BlockedDomain
    form_class = BlockedDomainForm
    template_name = 'cybersecurity/add_blocked_domain.html'
    success_url = reverse_lazy('cybersecurity:blocklist_management')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role in ['super_admin', 'provincial_admin']:
            messages.error(request, "You don't have permission to block domains.")
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.blocked_by = self.request.user
        
        response = super().form_valid(form)
        
        # Log the action
        AuditLog.log_action(
            user=self.request.user,
            action='create',
            asset=None,
            description=f"Blocked Domain: {form.instance.domain} - {form.instance.reason}",
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, f"Domain {form.instance.domain} has been blocked successfully.")
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


@login_required
@require_http_methods(["POST"])
def toggle_block_status(request, model_type, pk):
    """Toggle block status for IP or domain"""
    if not request.user.role in ['super_admin', 'provincial_admin']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if model_type == 'ip':
        item = get_object_or_404(BlockedIP, pk=pk)
        item_type = "IP"
    elif model_type == 'domain':
        item = get_object_or_404(BlockedDomain, pk=pk)
        item_type = "Domain"
    else:
        return JsonResponse({'error': 'Invalid model type'}, status=400)
    
    item.is_active = not item.is_active
    item.save()
    
    action = "unblocked" if not item.is_active else "blocked"
    
    # Log the action
    AuditLog.log_action(
        user=request.user,
        action='update',
        asset=None,
        description=f"{action} {item_type}: {getattr(item, 'ip_address', getattr(item, 'domain', ''))}",
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return JsonResponse({
        'success': True,
        'status': item.is_active,
        'message': f'{item_type} {action} successfully'
    })


@login_required
def blocklist_api(request):
    """API endpoint to get current active blocklist"""
    # Check for token authentication
    token = request.GET.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if token:
        try:
            agent_token = BranchAgentToken.objects.get(token=token, is_active=True)
            agent_token.update_last_sync()
        except BranchAgentToken.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=401)
    else:
        # For web requests, check if user is admin
        if not request.user.is_authenticated or not request.user.role in ['super_admin', 'provincial_admin']:
            return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get active blocklist
    blocked_ips = list(BlockedIP.objects.filter(is_active=True).values_list('ip_address', flat=True))
    blocked_domains = list(BlockedDomain.objects.filter(is_active=True).values_list('domain', flat=True))
    
    return JsonResponse({
        'blocked_ips': blocked_ips,
        'blocked_domains': blocked_domains,
        'timestamp': timezone.now().isoformat()
    })


@login_required
def agent_download(request):
    """Download page for the agent executable"""
    if not request.user.role in ['super_admin', 'provincial_admin']:
        messages.error(request, "You don't have permission to download the agent.")
        return redirect('dashboard:home')
    
    return render(request, 'cybersecurity/agent_download.html')


class SecurityIncidentListView(LoginRequiredMixin, ListView):
    """View to list security incidents"""
    model = SecurityIncident
    template_name = 'cybersecurity/security_incidents.html'
    context_object_name = 'incidents'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SecurityIncident.objects.select_related('asset', 'reported_by', 'resolved_by')
        
        # Filter by branch for non-admin users
        if not self.request.user.can_view_all_assets:
            queryset = queryset.filter(asset__branch=self.request.user.branch)
        
        # Apply filters
        severity_filter = self.request.GET.get('severity')
        type_filter = self.request.GET.get('type')
        status_filter = self.request.GET.get('status')
        
        if severity_filter:
            queryset = queryset.filter(severity=severity_filter)
        
        if type_filter:
            queryset = queryset.filter(incident_type=type_filter)
        
        if status_filter == 'resolved':
            queryset = queryset.filter(resolved=True)
        elif status_filter == 'unresolved':
            queryset = queryset.filter(resolved=False)
        
        return queryset.order_by('-date_reported')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate incident counts
        incidents = self.get_queryset()
        context['critical_incidents_count'] = incidents.filter(severity='critical').count()
        context['high_incidents_count'] = incidents.filter(severity='high').count()
        context['unresolved_incidents_count'] = incidents.filter(resolved=False).count()
        context['resolved_incidents_count'] = incidents.filter(resolved=True).count()
        
        # Add filter choices for template
        context['severity_choices'] = SecurityIncident.SEVERITY_CHOICES
        context['type_choices'] = SecurityIncident.INCIDENT_TYPE_CHOICES
        
        # Add current filter values
        context['current_severity'] = self.request.GET.get('severity', '')
        context['current_type'] = self.request.GET.get('type', '')
        context['current_status'] = self.request.GET.get('status', '')
        
        return context


class CreateSecurityIncidentView(LoginRequiredMixin, CreateView):
    """View to create a new security incident"""
    model = SecurityIncident
    form_class = SecurityIncidentForm
    template_name = 'cybersecurity/create_incident.html'
    success_url = reverse_lazy('cybersecurity:security_incidents')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        
        response = super().form_valid(form)
        
        # Log the action
        AuditLog.log_action(
            user=self.request.user,
            action='create',
            asset=form.instance.asset,
            description=f"Security incident reported: {form.instance.get_incident_type_display()} - {form.instance.description[:50]}",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, "Security incident has been reported successfully.")
        return response


@login_required
@require_http_methods(["POST"])
def resolve_incident(request, pk):
    """Resolve a security incident"""
    incident = get_object_or_404(SecurityIncident, pk=pk)
    
    # Check permissions
    if not request.user.can_view_all_assets and incident.asset.branch != request.user.branch:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    resolution_notes = request.POST.get('resolution_notes', '')
    incident.resolve(request.user, resolution_notes)
    
    # Log the action
    AuditLog.log_action(
        user=request.user,
        action='update',
        asset=incident.asset,
        description=f"Security incident resolved: {incident.get_incident_type_display()}",
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    messages.success(request, "Security incident has been resolved.")
    return redirect('cybersecurity:security_incidents')


@login_required
def login_analytics(request):
    """View to show login attempt analytics"""
    if not request.user.role in ['super_admin', 'provincial_admin']:
        messages.error(request, "You don't have permission to view security analytics.")
        return redirect('dashboard:home')
    
    # Get recent failed attempts
    recent_failed = LoginAttempt.objects.filter(
        success=False,
        timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
    ).order_by('-timestamp')[:20]
    
    # Get suspicious IPs (multiple failed attempts)
    suspicious_ips = LoginAttempt.objects.filter(
        success=False,
        timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
    ).values('ip_address').annotate(
        failed_count=Count('id')
    ).filter(failed_count__gte=3).order_by('-failed_count')
    
    context = {
        'recent_failed': recent_failed,
        'suspicious_ips': suspicious_ips,
        'total_blocked_ips': BlockedIP.objects.filter(is_active=True).count(),
        'total_blocked_domains': BlockedDomain.objects.filter(is_active=True).count(),
        'total_whitelisted_ips': WhitelistedIP.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'cybersecurity/login_analytics.html', context)


class WhitelistManagementView(LoginRequiredMixin, ListView):
    """View for managing whitelisted IP addresses"""
    template_name = 'cybersecurity/whitelist_management.html'
    context_object_name = 'whitelist_items'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role in ['super_admin', 'provincial_admin']:
            messages.error(request, 'Permission denied. Only Super Admins and Provincial Admins can manage whitelist.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return WhitelistedIP.objects.all().order_by('-date_added')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_whitelisted'] = WhitelistedIP.objects.filter(is_active=True).count()
        context['total_inactive'] = WhitelistedIP.objects.filter(is_active=False).count()
        return context


@login_required
@require_http_methods(["GET", "POST"])
def add_whitelisted_ip(request):
    """Add a new whitelisted IP address"""
    if not request.user.role in ['super_admin', 'provincial_admin']:
        messages.error(request, 'Permission denied. Only Super Admins and Provincial Admins can add whitelisted IPs.')
        return redirect('cybersecurity:whitelist')
    
    if request.method == 'POST':
        form = WhitelistedIPForm(request.POST)
        if form.is_valid():
            whitelisted_ip = form.save(commit=False)
            whitelisted_ip.added_by = request.user
            whitelisted_ip.save()
            
            # Log the action
            AuditLog.log_action(
                user=request.user,
                action='create',
                asset=None,
                description=f"Added IP to whitelist: {whitelisted_ip.ip_address} - {whitelisted_ip.reason}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f"IP {whitelisted_ip.ip_address} has been added to the whitelist.")
            return redirect('cybersecurity:whitelist')
    else:
        form = WhitelistedIPForm()
    
    return render(request, 'cybersecurity/add_whitelisted_ip.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def toggle_whitelist_status(request, pk):
    """Toggle whitelist status for IP"""
    if not request.user.role in ['super_admin', 'provincial_admin']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        whitelisted_ip = WhitelistedIP.objects.get(pk=pk)
        whitelisted_ip.is_active = not whitelisted_ip.is_active
        whitelisted_ip.save()
        
        action = "disabled" if not whitelisted_ip.is_active else "enabled"
        
        # Log the action
        AuditLog.log_action(
            user=request.user,
            action='update',
            asset=None,
            description=f"{action} whitelisted IP: {whitelisted_ip.ip_address}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'success': True,
            'is_active': whitelisted_ip.is_active,
            'message': f"Whitelisted IP {whitelisted_ip.ip_address} has been {action}."
        })
    except WhitelistedIP.DoesNotExist:
        return JsonResponse({'error': 'Whitelisted IP not found'}, status=404)

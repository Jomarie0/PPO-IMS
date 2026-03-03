from django.contrib import admin
from .models import BlockedIP, BlockedDomain, BranchAgentToken, LoginAttempt, SecurityIncident, WhitelistedIP


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'blocked_by', 'date_blocked', 'is_active']
    list_filter = ['is_active', 'date_blocked']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['date_blocked']
    actions = ['block_selected', 'unblock_selected']
    
    def block_selected(self, request, queryset):
        queryset.update(is_active=True)
    block_selected.short_description = "Block selected IPs"
    
    def unblock_selected(self, request, queryset):
        queryset.update(is_active=False)
    unblock_selected.short_description = "Unblock selected IPs"


@admin.register(BlockedDomain)
class BlockedDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'reason', 'blocked_by', 'date_blocked', 'is_active']
    list_filter = ['is_active', 'date_blocked']
    search_fields = ['domain', 'reason']
    readonly_fields = ['date_blocked']
    actions = ['block_selected', 'unblock_selected']
    
    def block_selected(self, request, queryset):
        queryset.update(is_active=True)
    block_selected.short_description = "Block selected domains"
    
    def unblock_selected(self, request, queryset):
        queryset.update(is_active=False)
    unblock_selected.short_description = "Unblock selected domains"


@admin.register(BranchAgentToken)
class BranchAgentTokenAdmin(admin.ModelAdmin):
    list_display = ['branch', 'token', 'last_sync', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['branch__name']
    readonly_fields = ['token', 'created_at', 'last_sync']
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        queryset.update(is_active=True)
    activate_selected.short_description = "Activate selected tokens"
    
    def deactivate_selected(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_selected.short_description = "Deactivate selected tokens"


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'success', 'timestamp', 'username_attempted']
    list_filter = ['success', 'timestamp']
    search_fields = ['user__username', 'ip_address', 'username_attempted']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    list_display = ['asset', 'incident_type', 'severity', 'resolved', 'date_reported', 'reported_by']
    list_filter = ['incident_type', 'severity', 'resolved', 'date_reported']
    search_fields = ['asset__property_number', 'description']
    readonly_fields = ['date_reported']
    date_hierarchy = 'date_reported'
    actions = ['resolve_selected']
    
    def resolve_selected(self, request, queryset):
        queryset.update(resolved=True, resolved_by=request.user)
    resolve_selected.short_description = "Mark selected incidents as resolved"


@admin.register(WhitelistedIP)
class WhitelistedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'added_by', 'date_added', 'is_active']
    list_filter = ['is_active', 'date_added', 'added_by']
    search_fields = ['ip_address', 'reason']
    list_editable = ['is_active']
    readonly_fields = ['date_added']
    date_hierarchy = 'date_added'
    actions = ['disable_selected', 'enable_selected']
    
    def disable_selected(self, request, queryset):
        queryset.update(is_active=False)
    disable_selected.short_description = "Disable selected whitelisted IPs"
    
    def enable_selected(self, request, queryset):
        queryset.update(is_active=True)
    enable_selected.short_description = "Enable selected whitelisted IPs"

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from assets.models import Asset
from branches.models import Branch
from cybersecurity.models import BlockedIP, BlockedDomain, SecurityIncident, LoginAttempt
import json

@login_required
def dashboard_home(request):
    """
    Main dashboard view with enhanced role-based data
    """
    user = request.user
    
    if user.role in ['super_admin', 'provincial_admin']:
        return provincial_dashboard(request)
    elif user.role in ['main_branch_admin', 'branch_admin', 'viewer']:
        # Check if user has required branch assignment
        if user.branch:
            return branch_dashboard(request)
        else:
            return render(request, 'dashboard/dashboard.html', {
                'error': f"User '{getattr(user, 'username', 'UNKNOWN')}' has role '{user.get_role_display() if hasattr(user, 'get_role_display') else user.role}' but no branch assigned. Please contact administrator to assign a branch."
            })
    else:
        # Fallback for any other role or missing role
        return render(request, 'dashboard/dashboard.html', {
            'error': f"Unknown role '{getattr(user, 'role', 'NO_ROLE')}' for user '{getattr(user, 'username', 'UNKNOWN')}'. Please contact administrator."
        })

def provincial_dashboard(request):
    """
    Provincial Admin Dashboard - shows data from all branches
    """
    # Total statistics
    total_assets = Asset.objects.count()
    active_assets = Asset.objects.filter(status='active').count()
    under_repair_assets = Asset.objects.filter(status='under_repair').count()
    missing_assets = Asset.objects.filter(status='missing').count()
    condemned_assets = Asset.objects.filter(status='condemned').count()
    
    # Security statistics
    total_blocked_ips = BlockedIP.objects.filter(is_active=True).count()
    total_blocked_domains = BlockedDomain.objects.filter(is_active=True).count()
    
    # Failed login attempts in last 24 hours
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    failed_logins_24h = LoginAttempt.objects.filter(
        success=False,
        timestamp__gte=twenty_four_hours_ago
    ).count()
    
    # Security incidents
    total_incidents = SecurityIncident.objects.count()
    unresolved_incidents = SecurityIncident.objects.filter(resolved=False).count()
    critical_incidents = SecurityIncident.objects.filter(severity='critical', resolved=False).count()
    
    # Security compliance statistics
    assets_with_antivirus = Asset.objects.filter(antivirus_installed=True).count()
    assets_with_firewall = Asset.objects.filter(firewall_enabled=True).count()
    assets_with_encryption = Asset.objects.filter(disk_encrypted=True).count()
    
    # Calculate average compliance score
    compliance_scores = []
    for asset in Asset.objects.all():
        compliance_scores.append(asset.compliance_score)
    avg_compliance_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
    
    # Risk level distribution
    risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
    for asset in Asset.objects.all():
        risk_distribution[asset.risk_level] += 1
    
    # Branch statistics
    branch_stats = []
    for branch in Branch.objects.filter(is_active=True):
        stats = {
            'name': branch.name,
            'code': branch.code,
            'total': branch.asset_count,
            'active': branch.active_assets,
            'under_repair': branch.under_repair_assets,
            'missing': branch.missing_assets,
            'condemned': branch.condemned_assets,
        }
        branch_stats.append(stats)
    
    # Most damaged branch (highest under_repair + missing)
    most_damaged = None
    max_damage = 0
    for stats in branch_stats:
        damage_count = stats['under_repair'] + stats['missing']
        if damage_count > max_damage:
            max_damage = damage_count
            most_damaged = stats
    
    # Recently added assets (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_assets = Asset.objects.filter(
        created_at__date__gte=thirty_days_ago
    ).select_related('branch').order_by('-created_at')[:10]
    
    # Asset type distribution
    asset_type_data = Asset.objects.values('asset_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent security incidents
    recent_incidents = SecurityIncident.objects.select_related(
        'asset', 'reported_by'
    ).order_by('-date_reported')[:5]
    
    # Prepare data for charts
    branch_comparison_data = {
        'labels': [stats['name'] for stats in branch_stats],
        'total': [stats['total'] for stats in branch_stats],
        'active': [stats['active'] for stats in branch_stats],
        'under_repair': [stats['under_repair'] for stats in branch_stats],
        'missing': [stats['missing'] for stats in branch_stats],
        'condemned': [stats['condemned'] for stats in branch_stats],
    }
    
    asset_type_distribution = {
        'labels': [item['asset_type'].replace('_', ' ').title() for item in asset_type_data],
        'data': [item['count'] for item in asset_type_data],
    }
    
    risk_level_distribution = {
        'labels': list(risk_distribution.keys()),
        'data': list(risk_distribution.values()),
        'colors': ['#28a745', '#ffc107', '#dc3545', '#343a40']
    }
    
    context = {
        'user_role': 'provincial_admin',
        'total_assets': total_assets,
        'active_assets': active_assets,
        'under_repair_assets': under_repair_assets,
        'missing_assets': missing_assets,
        'condemned_assets': condemned_assets,
        'branch_stats': branch_stats,
        'most_damaged_branch': most_damaged,
        'recent_assets': recent_assets,
        'branch_comparison_data': json.dumps(branch_comparison_data),
        'asset_type_distribution': json.dumps(asset_type_distribution),
        # Security data
        'total_blocked_ips': total_blocked_ips,
        'total_blocked_domains': total_blocked_domains,
        'failed_logins_24h': failed_logins_24h,
        'total_incidents': total_incidents,
        'unresolved_incidents': unresolved_incidents,
        'critical_incidents': critical_incidents,
        'avg_compliance_score': round(avg_compliance_score, 1),
        'assets_with_antivirus': assets_with_antivirus,
        'assets_with_firewall': assets_with_firewall,
        'assets_with_encryption': assets_with_encryption,
        'risk_level_distribution': json.dumps(risk_level_distribution),
        'recent_incidents': recent_incidents,
    }
    
    return render(request, 'dashboard/provincial_dashboard.html', context)

def branch_dashboard(request):
    """
    Branch Dashboard - shows data for the user's branch only
    """
    user = request.user
    branch = user.branch
    
    if not branch:
        return render(request, 'dashboard/dashboard.html', {'error': 'No branch assigned'})
    
    # Branch statistics
    total_assets = branch.asset_count
    active_assets = branch.active_assets
    under_repair_assets = branch.under_repair_assets
    missing_assets = branch.missing_assets
    condemned_assets = branch.condemned_assets
    
    # Recently added assets for this branch
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_assets = Asset.objects.filter(
        branch=branch,
        created_at__date__gte=thirty_days_ago
    ).order_by('-created_at')[:10]
    
    # Asset type distribution for this branch
    asset_type_data = Asset.objects.filter(
        branch=branch
    ).values('asset_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Assets under warranty
    assets_under_warranty = Asset.objects.filter(
        branch=branch,
        warranty_expiration__gte=timezone.now().date()
    ).count()
    
    # Assets expiring soon (next 90 days)
    ninety_days_from_now = timezone.now().date() + timedelta(days=90)
    warranty_expiring_soon = Asset.objects.filter(
        branch=branch,
        warranty_expiration__lte=ninety_days_from_now,
        warranty_expiration__gte=timezone.now().date()
    ).count()
    
    # Prepare data for pie chart
    status_distribution = {
        'labels': ['Active', 'Under Repair', 'Missing', 'Condemned'],
        'data': [active_assets, under_repair_assets, missing_assets, condemned_assets],
        'colors': ['#28a745', '#ffc107', '#dc3545', '#6c757d']
    }
    
    asset_type_distribution = {
        'labels': [item['asset_type'].replace('_', ' ').title() for item in asset_type_data],
        'data': [item['count'] for item in asset_type_data],
    }
    
    context = {
        'user_role': user.role,
        'branch': branch,
        'total_assets': total_assets,
        'active_assets': active_assets,
        'under_repair_assets': under_repair_assets,
        'missing_assets': missing_assets,
        'condemned_assets': condemned_assets,
        'recent_assets': recent_assets,
        'assets_under_warranty': assets_under_warranty,
        'warranty_expiring_soon': warranty_expiring_soon,
        'status_distribution': json.dumps(status_distribution),
        'asset_type_distribution': json.dumps(asset_type_distribution),
    }
    
    return render(request, 'dashboard/branch_dashboard.html', context)

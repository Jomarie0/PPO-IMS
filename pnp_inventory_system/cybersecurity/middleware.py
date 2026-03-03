from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.utils import timezone
from .models import LoginAttempt, BlockedIP, BlockedDomain, WhitelistedIP
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware to handle:
    1. IP blocking
    2. Domain blocking
    3. Login attempt tracking
    4. Automatic IP blocking after failed attempts
    """
    
    def process_request(self, request):
        """Check if IP or domain is blocked before processing request"""
        ip_address = self.get_client_ip(request)
        
        # Check if IP is whitelisted (whitelist takes precedence)
        if WhitelistedIP.objects.filter(ip_address=ip_address, is_active=True).exists():
            logger.info(f"Whitelisted IP allowed: {ip_address}")
            return None
        
        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip_address, is_active=True).exists():
            logger.warning(f"Blocked IP attempted access: {ip_address}")
            return HttpResponseForbidden("Access denied. Your IP address has been blocked.")
        
        # Check if domain is blocked
        host = self.get_host_from_request(request)
        if self.is_domain_blocked(host):
            logger.warning(f"Blocked domain attempted access: {host}")
            return HttpResponseForbidden("Access denied. This domain has been blocked.")
        
        return None
    
    def process_response(self, request, response):
        """Track login attempts"""
        # Only process login attempts
        if request.path == '/users/login/' and request.method == 'POST':
            self.track_login_attempt(request)
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_host_from_request(self, request):
        """Extract host from request"""
        # Get the host from the request
        host = request.get_host()
        
        # Remove port if present
        if ':' in host:
            host = host.split(':')[0]
        
        # Remove www. prefix for consistent checking
        if host.startswith('www.'):
            host = host[4:]
        
        return host.lower()
    
    def is_domain_blocked(self, host):
        """Check if domain or subdomain is blocked - SAFE VERSION"""
        if not host:
            return False
        
        # Normalize host (remove port, www, convert to lowercase)
        host = host.lower().split(':')[0]  # Remove port
        if host.startswith('www.'):
            host = host[4:]  # Remove www.
        
        # Check exact match first (most reliable)
        if BlockedDomain.objects.filter(domain=host, is_active=True).exists():
            return True
        
        # Check if this is a subdomain of a blocked domain
        # Only block direct subdomains, not partial matches
        # Use efficient query instead of loading all domains
        blocked_domains = BlockedDomain.objects.filter(is_active=True).values_list('domain', flat=True)
        
        for blocked_domain in blocked_domains:
            blocked_domain = blocked_domain.lower()
            
            # Extract main domain from both for comparison
            host_main = self.extract_main_domain(host)
            blocked_main = self.extract_main_domain(blocked_domain)
            
            # Block if main domains match exactly
            if host_main and blocked_main and host_main == blocked_main:
                return True
        
        return False
    
    def extract_main_domain(self, domain):
        """Extract main domain from domain string - SAFE VERSION"""
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        parts = domain.split('.')
        if len(parts) < 2:
            return domain
        
        # Handle common TLDs properly
        if len(parts) == 2:
            return '.'.join(parts)  # example.com
        elif len(parts) >= 3:
            # Check if last part is a known TLD
            known_tlds = ['com', 'net', 'org', 'gov', 'ph', 'edu', 'mil']
            if parts[-1] in known_tlds:
                return '.'.join(parts[-2:])  # example.com.ph -> example.com.ph
            else:
                return '.'.join(parts[-2:])  # sub.example.com -> example.com
        else:
            return domain
    
    def track_login_attempt(self, request):
        """Track login attempt and auto-block IPs with too many failures"""
        ip_address = self.get_client_ip(request)
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Try to authenticate
        user = authenticate(request, username=username, password=password)
        success = user is not None
        
        # Log the login attempt
        login_attempt = LoginAttempt.objects.create(
            user=user if success else None,
            ip_address=ip_address,
            success=success,
            user_agent=user_agent,
            username_attempted=username if not success else ''
        )
        
        # If login failed, check for auto-blocking
        if not success:
            self.check_and_block_ip(ip_address)
        
        logger.info(f"Login attempt tracked: {success} for {username} from {ip_address}")
    
    def check_and_block_ip(self, ip_address):
        """Check if IP should be blocked based on failed attempts"""
        # First check if IP is whitelisted
        if WhitelistedIP.objects.filter(ip_address=ip_address, is_active=True).exists():
            logger.info(f"IP is whitelisted, skipping auto-block: {ip_address}")
            return
        
        # Count failed attempts in the last hour
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        failed_attempts = LoginAttempt.objects.filter(
            ip_address=ip_address,
            success=False,
            timestamp__gte=one_hour_ago
        ).count()
        
        # If 10 or more failed attempts, block the IP (increased from 5 for development)
        if failed_attempts >= 10:
            # Use get_or_create to avoid duplicate errors
            blocked_ip, created = BlockedIP.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'reason': 'Automatic block: Too many failed login attempts',
                    'blocked_by': None  # System-generated block
                }
            )
            
            if created:
                logger.warning(f"IP automatically blocked due to failed attempts: {ip_address}")
            else:
                # IP was already blocked, just ensure it's active
                if not blocked_ip.is_active:
                    blocked_ip.is_active = True
                    blocked_ip.save()
                    logger.warning(f"IP re-activated due to failed attempts: {ip_address}")


class LoginAttemptMiddleware(MiddlewareMixin):
    """
    Separate middleware to track all login attempts (including successful ones)
    This ensures we capture successful logins for audit purposes
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Track login attempts before view is processed"""
        if request.path == '/users/login/' and request.method == 'POST':
            # This will be handled by SecurityMiddleware
            pass
        return None

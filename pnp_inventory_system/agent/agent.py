#!/usr/bin/env python3
"""
PNP Security Agent v1.0
Simple agent for testing domain/IP blocking functionality
"""

import requests
import os
import sys
import time
import json
from datetime import datetime

class PNPSecurityAgent:
    def __init__(self, server_url, token):
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.api_endpoint = f"{self.server_url}/cybersecurity/api/blocklist/"
        self.last_sync = None
        
    def sync_blocklist(self):
        """Sync blocklist from server"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(self.api_endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.apply_blocklist(data)
                self.last_sync = datetime.now()
                print(f"✅ Sync successful at {self.last_sync}")
                return True
            else:
                print(f"❌ Sync failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Sync error: {e}")
            return False
    
    def apply_blocklist(self, data):
        """Apply blocklist to local system"""
        blocked_ips = data.get('blocked_ips', [])
        blocked_domains = data.get('blocked_domains', [])
        
        print(f"📊 Received {len(blocked_ips)} IPs and {len(blocked_domains)} domains")
        
        # For Windows, we could update hosts file
        # For testing, we'll just log what would be blocked
        print("\n🔒 Blocked IPs:")
        for ip in blocked_ips:
            print(f"  - {ip}")
        
        print("\n🌐 Blocked Domains:")
        for domain in blocked_domains:
            print(f"  - {domain}")
    
    def start_monitoring(self, interval=300):  # 5 minutes
        """Start continuous monitoring"""
        print(f"🚀 Starting PNP Security Agent")
        print(f"📡 Server: {self.server_url}")
        print(f"🔑 Token: {self.token[:8]}...")
        print(f"⏰ Sync interval: {interval} seconds")
        print("=" * 50)
        
        # Initial sync
        self.sync_blocklist()
        
        # Continuous monitoring
        while True:
            try:
                time.sleep(interval)
                self.sync_blocklist()
            except KeyboardInterrupt:
                print("\n🛑 Agent stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retry

def main():
    """Main function for testing"""
    print("🛡️  PNP Security Agent v1.0 - Test Version")
    print("=" * 50)
    
    # Configuration - you can modify these for testing
    SERVER_URL = "http://127.0.0.1:8000"
    TOKEN = "your-test-token-here"  # Replace with actual token
    
    if len(sys.argv) > 1:
        TOKEN = sys.argv[1]  # Allow token as command line argument
    
    if TOKEN == "your-test-token-here":
        print("\n❌ Please provide a valid token:")
        print("   python agent.py YOUR_TOKEN_HERE")
        print("   or generate token with: python manage.py generate_tokens")
        return
    
    # Create and start agent
    agent = PNPSecurityAgent(SERVER_URL, TOKEN)
    
    # For testing, run only once
    if len(sys.argv) > 2 and sys.argv[2] == "--test":
        print("🧪 Running in test mode (single sync)")
        agent.sync_blocklist()
    else:
        print("🔄 Running in continuous mode (Ctrl+C to stop)")
        agent.start_monitoring()

if __name__ == "__main__":
    main()

# PNP Security Agent v1.0

## 📋 OVERVIEW

The PNP Security Agent provides real-time protection for PNP workstations by synchronizing with the central blocklist server.

## 🚀 QUICK START

### 1. Generate Token
```bash
# In Django project directory
python manage.py generate_tokens --branch YOUR_BRANCH_CODE
```

### 2. Test Agent
```bash
# Navigate to agent directory
cd agent

# Test with your token
python agent.py YOUR_TOKEN_HERE --test
```

### 3. Build Executable
```bash
# Build the agent
python build_exe.py

# This creates: dist/PNP_Security_Agent.exe
```

### 4. Deploy Agent
```bash
# Copy to workstation
copy dist/PNP_Security_Agent.exe C:\\PNP_Agent\\

# Run with token
PNP_Security_Agent.exe YOUR_TOKEN_HERE
```

## 🛡️ FEATURES

- **Real-time Sync**: Updates blocklist every 5 minutes
- **IP Blocking**: Blocks malicious IP addresses
- **Domain Blocking**: Blocks access to malicious domains
- **Token Authentication**: Secure API communication
- **Logging**: Comprehensive activity logging
- **Background Service**: Runs continuously in background

## ⚙️ CONFIGURATION

### Environment Variables (Optional)
```bash
# Set server URL (default: http://127.0.0.1:8000)
PNP_SERVER_URL=https://your-pnp-server.com

# Set sync interval in seconds (default: 300)
PNP_SYNC_INTERVAL=300
```

### Command Line Options
```bash
# Run with token
PNP_Security_Agent.exe YOUR_TOKEN

# Test single sync
PNP_Security_Agent.exe YOUR_TOKEN --test

# Run with custom server
PNP_Security_Agent.exe YOUR_TOKEN --server https://custom-server.com
```

## 🔧 BUILD REQUIREMENTS

### Development
```bash
pip install requests pyinstaller
```

### Production
- Windows 10/11
- Network connectivity to PNP server
- Administrator privileges (for hosts file modification)

## 📁 FILE STRUCTURE

```
agent/
├── agent.py           # Main agent script
├── build_exe.py       # Build script
├── README.md          # This file
├── dist/              # Built executables
│   └── PNP_Security_Agent.exe
└── install.bat         # Installation script
```

## 🧪 TESTING

### Test Server Connection
```bash
# Test API connectivity
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/cybersecurity/api/blocklist/
```

### Test Agent Functionality
```bash
# Run in test mode
python agent.py YOUR_TOKEN --test

# Expected output:
# ✅ Sync successful at 2026-03-03 10:15:00
# 📊 Received 5 IPs and 3 domains
# 🔒 Blocked IPs: [list of IPs]
# 🌐 Blocked Domains: [list of domains]
```

## 🚨 DEPLOYMENT

### Manual Installation
1. Copy `PNP_Security_Agent.exe` to workstation
2. Run as Administrator
3. Enter branch token when prompted
4. Verify connection in logs

### Automated Installation
1. Use `install.bat` for silent deployment
2. Configure via Group Policy for enterprise deployment
3. Monitor via PNP dashboard

## 🔒 SECURITY CONSIDERATIONS

- **Token Protection**: Store tokens securely
- **Network Access**: Requires outbound HTTPS/HTTP to server
- **Local Admin**: Needs admin rights for hosts file modification
- **Logging**: All activities logged locally and centrally

## 📞 SUPPORT

For issues or questions:
1. Check agent logs for error messages
2. Verify network connectivity to PNP server
3. Validate token is active and correct
4. Contact PNP system administrator

## 🔄 UPDATES

The agent automatically syncs with the server every 5 minutes. Updates to blocklist are applied immediately without requiring agent restart.

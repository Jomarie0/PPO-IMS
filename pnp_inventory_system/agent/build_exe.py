"""
Build script to create PNP Security Agent executable
Requires: pip install pyinstaller
"""

import os
import sys
import subprocess

def build_agent():
    """Build the agent executable"""
    print("🔨 Building PNP Security Agent...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller
        print("✅ PyInstaller installed")
    
    # Build options
    build_command = [
        "pyinstaller",
        "--onefile",           # Create single executable
        "--windowed",          # No console window (for production)
        "--name=PNP_Security_Agent",  # Output name
        "--icon=icon.ico",      # Icon (if available)
        "--add-data=README.md;.",  # Include additional files
        "agent.py"
    ]
    
    # For testing, show console
    build_command[2] = "--console"
    
    print("🔨 Building executable...")
    try:
        result = subprocess.run(build_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print(f"📁 Executable location: dist/PNP_Security_Agent.exe")
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"❌ Build error: {e}")

def create_installer():
    """Create a simple installer script"""
    installer_script = """@echo off
echo Installing PNP Security Agent...
echo.
echo Please close this window after installation is complete.
echo.
mkdir "C:\\Program Files\\PNP Security Agent" 2>nul
copy "PNP_Security_Agent.exe" "C:\\Program Files\\PNP Security Agent\\" 2>nul
if exist "C:\\Program Files\\PNP Security Agent\\PNP_Security_Agent.exe" (
    echo ✅ Installation successful!
    echo The agent has been installed to: C:\\Program Files\\PNP Security Agent
    echo.
    echo To configure the agent:
    echo 1. Get your branch token from the PNP system administrator
    echo 2. Run: PNP_Security_Agent.exe YOUR_TOKEN_HERE
    echo.
) else (
    echo ❌ Installation failed!
    pause
)
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_script)
    
    print("✅ Created install.bat")

if __name__ == "__main__":
    print("🛡️  PNP Security Agent Build Tool")
    print("=" * 40)
    
    # Create agent directory if it doesn't exist
    if not os.path.exists("agent"):
        os.makedirs("agent")
        print("📁 Created agent directory")
    
    # Change to agent directory
    os.chdir("agent")
    
    # Build the executable
    build_agent()
    
    # Create installer
    create_installer()
    
    print("\n🎉 Build process completed!")
    print("\n📋 Next steps:")
    print("1. Test the executable: dist/PNP_Security_Agent.exe")
    print("2. Run with token: PNP_Security_Agent.exe YOUR_TOKEN")
    print("3. Use install.bat for deployment")

"""
Setup script for AI Employee Gold Tier system

This script installs required dependencies and sets up session directories
for all watcher scripts.
"""

import os
import subprocess
import sys
from pathlib import Path

def install_playwright_browsers():
    """Install required Playwright browsers"""
    print("Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("Playwright browsers installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright browsers: {e}")
        return False

def create_session_directories():
    """Create session directories for all watchers"""
    base_path = Path(__file__).parent

    session_dirs = [
        base_path / 'linkedin_session',
        base_path / 'whatsapp_session'
    ]

    for session_dir in session_dirs:
        session_dir.mkdir(exist_ok=True)
        print(f"Created session directory: {session_dir}")

    # Also create other necessary directories
    (base_path / 'Needs_Action').mkdir(exist_ok=True)
    (base_path / 'Pending_Approval').mkdir(exist_ok=True)
    (base_path / 'Approved').mkdir(exist_ok=True)
    (base_path / 'Done').mkdir(exist_ok=True)
    (base_path / 'Inbox').mkdir(exist_ok=True)

    print("Created required directories")

def install_requirements():
    """Install Python requirements"""
    requirements_path = Path(__file__).parent / 'requirements.txt'

    if requirements_path.exists():
        print("Installing Python requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)], check=True)
            print("Requirements installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            return False
    else:
        print("No requirements.txt found in current directory")
        return False

def main():
    print("AI Employee Gold Tier Setup")
    print("=" * 40)

    # Install requirements
    requirements_ok = install_requirements()

    # Install Playwright browsers
    browsers_ok = install_playwright_browsers()

    # Create session directories
    create_session_directories()

    print("\nSetup Summary:")
    print(f"Requirements: {'✓' if requirements_ok else '✗'}")
    print(f"Playwright browsers: {'✓' if browsers_ok else '✗'}")

    if requirements_ok and browsers_ok:
        print("\nSetup completed successfully!")
        print("You can now run the watchers individually to set up authentication:")
        print("- python linkedin_watcher.py (first time will require manual login)")
        print("- python whatsapp_watcher.py (first time will require QR code scan)")
        print("- python test_runner.py to verify all watchers work in test mode")
        return 0
    else:
        print("\nSetup had issues. Please fix errors before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
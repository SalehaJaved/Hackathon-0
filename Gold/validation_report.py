"""
Validation Report for AI Employee Watchers

This script provides a structured validation report for the AI Employee system:
- LinkedIn Auth: PASS/FAIL
- WhatsApp Session: PASS/FAIL
- Playwright Install: PASS/FAIL
- Session Persistence: PASS/FAIL
- MCP Connectivity: PASS/FAIL
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
import json

def check_playwright_install():
    """Check if Playwright is properly installed"""
    try:
        import playwright
        from playwright.sync_api import sync_playwright
        return True, "Playwright is properly installed"
    except ImportError:
        return False, "Playwright not found"
    except Exception as e:
        return False, f"Playwright error: {str(e)}"

def check_chromium_install():
    """Check if Chromium is properly installed for Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True, "Chromium is properly installed and accessible"
    except Exception as e:
        return False, f"Chromium error: {str(e)}"

def check_linkedin_auth():
    """Check if LinkedIn session directory exists and is properly configured"""
    session_path = Path(__file__).parent / 'linkedin_session'
    if session_path.exists():
        files = list(session_path.iterdir())
        if len(files) > 0:
            return True, f"LinkedIn session directory exists with {len(files)} files"
    return False, "LinkedIn session directory does not exist or is empty"

def check_whatsapp_session():
    """Check if WhatsApp session directory exists and is properly configured"""
    session_path = Path(__file__).parent / 'whatsapp_session'
    if session_path.exists():
        files = list(session_path.iterdir())
        if len(files) > 0:
            return True, f"WhatsApp session directory exists with {len(files)} files"
    return False, "WhatsApp session directory does not exist or is empty"

def check_mcp_connectivity():
    """Check if MCP servers are properly configured"""
    mcp_config_path = Path(__file__).parent / 'mcp_config.json'
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
            if 'servers' in config and len(config['servers']) > 0:
                return True, "MCP configuration exists and has servers defined"
        except:
            pass
    elif mcp_config_path.exists():
        return True, "MCP configuration file exists"
    else:
        # Check if mcp servers are running by looking for the server files
        email_server = Path(__file__).parent / 'mcp_servers' / 'email_mcp_server.py'
        social_server = Path(__file__).parent / 'mcp_servers' / 'social_media_mcp_server.py'
        if email_server.exists() and social_server.exists():
            return True, "MCP servers found (email and social media)"
    return False, "MCP configuration not properly set up"

def check_session_persistence():
    """Check session persistence configuration across all watchers"""
    all_sessions_exist = True
    session_status = []

    # Check LinkedIn session
    linkedin_session = Path(__file__).parent / 'linkedin_session'
    if linkedin_session.exists():
        session_status.append(f"LinkedIn session exists: {len(list(linkedin_session.iterdir()))} files")
    else:
        session_status.append("LinkedIn session missing")
        all_sessions_exist = False

    # Check WhatsApp session
    whatsapp_session = Path(__file__).parent / 'whatsapp_session'
    if whatsapp_session.exists():
        session_status.append(f"WhatsApp session exists: {len(list(whatsapp_session.iterdir()))} files")
    else:
        session_status.append("WhatsApp session missing")
        all_sessions_exist = False

    # Check if persistent context is used in code
    # Check LinkedIn watcher
    linkedin_watcher_path = Path(__file__).parent / 'linkedin_watcher.py'
    whatsapp_watcher_path = Path(__file__).parent / 'whatsapp_watcher.py'

    persistent_used = True
    if linkedin_watcher_path.exists():
        with open(linkedin_watcher_path, 'r') as f:
            content = f.read()
            if 'launch_persistent_context' not in content:
                persistent_used = False
                session_status.append("launch_persistent_context not used in LinkedIn watcher")

    if whatsapp_watcher_path.exists():
        with open(whatsapp_watcher_path, 'r') as f:
            content = f.read()
            if 'launch_persistent_context' not in content:
                persistent_used = False
                session_status.append("launch_persistent_context not used in WhatsApp watcher")

    if all_sessions_exist and persistent_used:
        return True, f"Session persistence properly configured: {', '.join(session_status)}"
    else:
        return False, f"Session persistence issues: {', '.join(session_status)}"

def main():
    print("AI Employee System Validation Report")
    print("=" * 60)

    # Check Playwright installation
    playwright_pass, playwright_msg = check_playwright_install()
    print(f"Playwright Install: {'PASS' if playwright_pass else 'FAIL'}")
    print(f"  Details: {playwright_msg}")

    # Check Chromium installation
    chromium_pass, chromium_msg = check_chromium_install()
    print(f"Chromium Install: {'PASS' if chromium_pass else 'FAIL'}")
    print(f"  Details: {chromium_msg}")

    # Check LinkedIn authentication
    linkedin_pass, linkedin_msg = check_linkedin_auth()
    print(f"LinkedIn Auth: {'PASS' if linkedin_pass else 'FAIL'}")
    print(f"  Details: {linkedin_msg}")

    # Check WhatsApp session
    whatsapp_pass, whatsapp_msg = check_whatsapp_session()
    print(f"WhatsApp Session: {'PASS' if whatsapp_pass else 'FAIL'}")
    print(f"  Details: {whatsapp_msg}")

    # Check session persistence
    session_pass, session_msg = check_session_persistence()
    print(f"Session Persistence: {'PASS' if session_pass else 'FAIL'}")
    print(f"  Details: {session_msg}")

    # Check MCP connectivity
    mcp_pass, mcp_msg = check_mcp_connectivity()
    print(f"MCP Connectivity: {'PASS' if mcp_pass else 'FAIL'}")
    print(f"  Details: {mcp_msg}")

    # Overall validation
    all_checks = [playwright_pass, chromium_pass, linkedin_pass, whatsapp_pass, session_pass, mcp_pass]
    passed_count = sum(all_checks)
    total_checks = len(all_checks)

    print("=" * 60)
    print(f"VALIDATION SUMMARY: {passed_count}/{total_checks} checks passed")

    if passed_count == total_checks:
        print("Overall Status: FULLY OPERATIONAL")
        return 0
    else:
        print("Overall Status: NEEDS ATTENTION")
        print("\nRecommendations:")
        if not playwright_pass or not chromium_pass:
            print("- Install Playwright: pip install playwright")
            print("- Install Playwright browsers: playwright install chromium")
        if not linkedin_pass:
            print("- Run LinkedIn watcher once to create session: python linkedin_watcher.py")
        if not whatsapp_pass:
            print("- Run WhatsApp watcher once to create session: python whatsapp_watcher.py")
        if not mcp_pass:
            print("- Check MCP server configuration and ensure servers are running")

        return 1

if __name__ == "__main__":
    sys.exit(main())
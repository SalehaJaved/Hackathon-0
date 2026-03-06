"""
System Health Monitor for Gold Tier AI Employee
Implements comprehensive monitoring and error recovery for all Gold tier requirements
"""

import os
import psutil
import time
from pathlib import Path
from datetime import datetime
import json
import subprocess
from typing import Dict, Any, List


def check_system_resources() -> Dict[str, Any]:
    """Check system resources (CPU, memory, disk)"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    status = "healthy"
    if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
        status = "critical"
    elif cpu_percent > 75 or memory.percent > 75 or disk.percent > 75:
        status = "warning"

    print(f"[SYSTEM] Resource Status: {status}")
    print(f"  -> CPU Usage: {cpu_percent}%")
    print(f"  -> Memory Usage: {memory.percent}% ({memory.available / (1024**3):.1f}GB available)")
    print(f"  -> Disk Usage: {disk.percent}% ({disk.free / (1024**3):.1f}GB free)")
    print()

    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "status": status
    }


def check_folder_status():
    """Check the status of all important folders including Gold tier additions"""
    base_dir = Path(__file__).parent

    folders = [
        'Inbox', 'Needs_Action', 'Plans', 'Pending_Approval',
        'Approved', 'Rejected', 'Done', 'Logs', 'Briefings',
        'Updates', 'Accounting', 'Invoices', 'RalphWiggumStates'
    ]

    print("[FOLDER] Folder Status:")
    all_ok = True
    for folder in folders:
        folder_path = base_dir / folder
        exists = folder_path.exists()
        file_count = len(list(folder_path.glob('*'))) if exists else 0
        status = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"  [{status}] {folder}: {'Exists' if exists else 'Missing'} ({file_count} items)")

    print(f"[FOLDER] Overall Status: {'HEALTHY' if all_ok else 'ISSUES FOUND'}")
    print()


def check_recent_files():
    """Check for recently created files in key folders"""
    base_dir = Path(__file__).parent

    key_folders = ['Needs_Action', 'Pending_Approval', 'Logs', 'Briefings', 'Accounting']

    print("[FILES] Recent Files (last 24 hours):")
    one_day_ago = datetime.now().timestamp() - 24*3600

    for folder in key_folders:
        folder_path = base_dir / folder
        if folder_path.exists():
            recent_files = []
            for file_path in folder_path.iterdir():
                if file_path.stat().st_mtime > one_day_ago:
                    recent_files.append(file_path.name)

            if recent_files:
                print(f"  {folder}: {len(recent_files)} recent files")
                for file in recent_files[:3]:  # Show first 3
                    print(f"    - {file}")
                if len(recent_files) > 3:
                    print(f"    - ... and {len(recent_files)-3} more")
            else:
                print(f"  {folder}: No recent files")
    print()


def check_process_status():
    """Check if key processes are running including Gold tier components"""
    print("[PROCESS] Process Status:")

    # Common process names for our AI Employee components
    ai_processes = [
        'filesystem_watcher', 'gmail_watcher', 'whatsapp_watcher',
        'scheduler', 'orchestrator', 'expense_policy_enforcer',
        'gold_tier_orchestrator', 'ralph_wiggum_loop'
    ]

    running_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name'].lower()
            proc_cmd = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''

            for ai_proc in ai_processes:
                if ai_proc in proc_name or ai_proc in proc_cmd:
                    running_processes.append((ai_proc, proc.info['pid']))
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if running_processes:
        for proc_name, pid in running_processes:
            print(f"  [RUNNING] {proc_name}: Running (PID: {pid})")
        print(f"[PROCESS] {len(running_processes)} AI Employee processes running")
    else:
        print("  [STOPPED] No AI Employee processes detected as running")
        print("  -> You may need to start the system with start_silver_ai_employee.bat")
    print()


def check_log_health():
    """Check for any errors in recent logs including audit logs"""
    base_dir = Path(__file__).parent
    logs_dir = base_dir / 'Logs'

    print("[LOGS] Log Health Check:")

    if not logs_dir.exists():
        print("  -> No Logs directory found")
        print()
        return

    # Check all log files for errors
    log_files = list(logs_dir.glob('*.json'))
    log_files.extend(logs_dir.glob('*.log'))

    if not log_files:
        print("  -> No log files found in Logs directory")
        print()
        return

    total_errors = 0
    total_warnings = 0
    error_files = []

    for log_file in log_files:
        file_errors = 0
        file_warnings = 0

        try:
            if log_file.suffix.lower() == '.json':
                # Try to parse as JSON logs
                with open(log_file, 'r', encoding='utf-8') as f:
                    try:
                        logs_data = json.load(f)
                        if isinstance(logs_data, list):
                            for entry in logs_data:
                                if isinstance(entry, dict):
                                    # Check for error status
                                    if entry.get('status') == 'failed' or 'error' in str(entry).lower():
                                        file_errors += 1
                                    elif entry.get('status') == 'warning' or 'warning' in str(entry).lower():
                                        file_warnings += 1
                        elif isinstance(logs_data, dict):
                            # Single log entry
                            if logs_data.get('status') == 'failed' or 'error' in str(logs_data).lower():
                                file_errors += 1
                            elif logs_data.get('status') == 'warning' or 'warning' in str(logs_data).lower():
                                file_warnings += 1
                    except json.JSONDecodeError:
                        # If it's not properly formatted JSON, try to read as text
                        f.seek(0)
                        content = f.read()
                        file_errors = content.lower().count('error')
                        file_warnings = content.lower().count('warning') + content.lower().count('warn')
            else:
                # Text log file
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_errors = content.lower().count('error')
                file_warnings = content.lower().count('warning') + content.lower().count('warn')

            if file_errors > 0 or file_warnings > 0:
                error_files.append((log_file.name, file_errors, file_warnings))

            total_errors += file_errors
            total_warnings += file_warnings

        except Exception as e:
            print(f"  [ERROR] Error reading log file {log_file.name}: {e}")

    print(f"  -> Total Error Count: {total_errors}")
    print(f"  -> Total Warning Count: {total_warnings}")
    print(f"  -> Log files with issues: {len(error_files)}")

    if total_errors == 0 and total_warnings == 0:
        print("  [OK] No errors or warnings in recent logs")
    elif total_errors > 0:
        print("  [ERROR] Errors detected in logs - check specific files for details")
        for file_name, errors, warnings in error_files[:3]:  # Show first 3 problem files
            print(f"    - {file_name}: {errors} errors, {warnings} warnings")
    elif total_warnings > 0:
        print("  [WARN] Warnings in logs - review as needed")

    print()


def check_mcp_servers():
    """Check MCP server status"""
    base_dir = Path(__file__).parent
    mcp_dir = base_dir / 'mcp_servers'

    print("[MCP] MCP Server Status:")

    if not mcp_dir.exists():
        print("  -> MCP servers directory not found")
        print()
        return

    server_dirs = [d for d in mcp_dir.iterdir() if d.is_dir()]

    print(f"  -> Found {len(server_dirs)} MCP server directories")

    for server_dir in server_dirs:
        print(f"  -> Server: {server_dir.name}")

        # Check for server implementation
        server_file = server_dir / f"{server_dir.name}_server.py"
        has_server = server_file.exists()
        print(f"     Server file: {'Y' if has_server else 'N'}")

        # Check for config
        config_file = server_dir / "config.json"
        has_config = config_file.exists()
        print(f"     Config file: {'Y' if has_config else 'N'}")

    print()


def check_gold_tier_features():
    """Check Gold tier specific features"""
    base_dir = Path(__file__).parent

    print("[GOLD] Gold Tier Feature Status:")

    # Check for Gold tier files
    gold_files = [
        ('gold_tier_orchestrator.py', 'Gold Tier Orchestrator'),
        ('ralph_wiggum_loop.py', 'Ralph Wiggum Loop'),
        ('audit_logger.py', 'Audit Logger'),
        ('mcp_config.json', 'MCP Configuration'),
        ('mcp_servers/email_mcp/email_mcp_server.py', 'Email MCP Server'),
        ('mcp_servers/social_media_mcp/social_media_mcp_server.py', 'Social Media MCP Server'),
        ('mcp_servers/browser_mcp/browser_mcp_server.py', 'Browser MCP Server')
    ]

    found_count = 0
    for file_path, description in gold_files:
        file_exists = (base_dir / file_path).exists()
        status = "Y" if file_exists else "N"
        print(f"  [{status}] {description}: {'Found' if file_exists else 'Missing'}")
        if file_exists:
            found_count += 1

    print(f"  -> Gold Tier Completion: {found_count}/{len(gold_files)} files")
    print()


def check_accounting_integration():
    """Check accounting system integration status"""
    base_dir = Path(__file__).parent
    accounting_dir = base_dir / 'Accounting'

    print("[ACCOUNTING] Accounting Integration Status:")

    if accounting_dir.exists():
        files = list(accounting_dir.glob('*'))
        print(f"  -> Accounting folder exists with {len(files)} files")

        # Check for common accounting file types
        json_files = list(accounting_dir.glob('*.json'))
        csv_files = list(accounting_dir.glob('*.csv'))
        print(f"    - JSON files: {len(json_files)}")
        print(f"    - CSV files: {len(csv_files)}")
    else:
        print("  -> Accounting folder does not exist")

    print()


def check_skill_files():
    """Check if all required skill files exist"""
    base_dir = Path(__file__).parent

    required_skills = [
        'process_needs_action_skill.md',
        'process_approval_skill.md',
        'business_audit_skill.md'
    ]

    print("[SKILLS] Skill Files Status:")
    for skill in required_skills:
        skill_path = base_dir / skill
        exists = skill_path.exists()
        status = "FOUND" if exists else "MISSING"
        print(f"  [{status}] {skill}: {'Found' if exists else 'Missing'}")
    print()


def main():
    print("="*60)
    print("   Personal AI Employee - Gold Tier System Monitor")
    print("="*60)
    print(f"   Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()

    # Gold tier enhanced checks
    check_system_resources()
    check_folder_status()
    check_recent_files()
    check_process_status()
    check_log_health()
    check_mcp_servers()
    check_gold_tier_features()
    check_accounting_integration()
    check_skill_files()

    print("="*60)
    print("   Gold Tier System Health Check Complete")
    print("="*60)


if __name__ == "__main__":
    main()
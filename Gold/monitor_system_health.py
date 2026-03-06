"""
System Health Monitor for the Personal AI Employee Silver Tier

This script checks the health and status of all Silver tier components.
"""

import os
import psutil
import time
from pathlib import Path
from datetime import datetime
import json


def check_folder_status():
    """Check the status of all important folders"""
    base_dir = Path(__file__).parent

    folders = [
        'Inbox', 'Needs_Action', 'Plans', 'Pending_Approval',
        'Approved', 'Rejected', 'Done', 'Logs', 'Briefings',
        'Updates', 'Accounting', 'Invoices'
    ]

    print("[FOLDER] Folder Status:")
    for folder in folders:
        folder_path = base_dir / folder
        exists = folder_path.exists()
        file_count = len(list(folder_path.glob('*'))) if exists else 0
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {folder}: {'Exists' if exists else 'Missing'} ({file_count} items)")
    print()


def check_recent_files():
    """Check for recently created files in key folders"""
    base_dir = Path(__file__).parent

    key_folders = ['Needs_Action', 'Pending_Approval', 'Logs', 'Briefings']

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
    """Check if key processes are running"""
    print("[PROCESS] Process Status:")

    # Common process names for our AI Employee components
    ai_processes = [
        'filesystem_watcher', 'gmail_watcher', 'whatsapp_watcher',
        'scheduler', 'orchestrator', 'expense_policy_enforcer'
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
    else:
        print("  [STOPPED] No AI Employee processes detected as running")
        print("  -> You may need to start the system with start_silver_ai_employee.bat")
    print()


def check_log_health():
    """Check for any errors in recent logs"""
    base_dir = Path(__file__).parent
    logs_dir = base_dir / 'Logs'

    print("[LOGS] Log Health Check:")

    if not logs_dir.exists():
        print("  -> No Logs directory found")
        print()
        return

    # Check the most recent log file
    log_files = list(logs_dir.glob('*.json'))
    log_files.extend(logs_dir.glob('*.log'))

    if not log_files:
        print("  -> No log files found in Logs directory")
        print()
        return

    # Get the most recent log file
    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)

    error_count = 0
    warning_count = 0

    try:
        if latest_log.suffix.lower() == '.json':
            # Try to parse as JSON logs
            with open(latest_log, 'r', encoding='utf-8') as f:
                try:
                    logs_data = json.load(f)
                    if isinstance(logs_data, list):
                        for entry in logs_data:
                            if isinstance(entry, dict):
                                level = entry.get('level', '').upper()
                                if 'ERROR' in level or level == 'ERROR':
                                    error_count += 1
                                elif 'WARNING' in level or 'WARN' in level:
                                    warning_count += 1
                except json.JSONDecodeError:
                    # Not a JSON log file, skip
                    pass
        else:
            # Text log file
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
                error_count = content.lower().count('error')
                warning_count = content.lower().count('warning') + content.lower().count('warn')

        print(f"  -> Checking: {latest_log.name}")
        print(f"  -> Errors found: {error_count}")
        print(f"  -> Warnings found: {warning_count}")

        if error_count == 0 and warning_count == 0:
            print("  [OK] No errors or warnings in recent logs")
        elif error_count > 0:
            print("  [ERROR] Errors detected in logs - check log file for details")
        elif warning_count > 0:
            print("  [WARN] Warnings in logs - review as needed")

    except Exception as e:
        print(f"  [ERROR] Error reading log file: {e}")

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
    print("   Personal AI Employee - Silver Tier System Monitor")
    print("="*60)
    print(f"   Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()

    check_folder_status()
    check_recent_files()
    check_process_status()
    check_log_health()
    check_skill_files()

    print("="*60)
    print("   System Health Check Complete")
    print("="*60)


if __name__ == "__main__":
    main()
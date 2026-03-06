@echo off
echo =====================================================
echo     Personal AI Employee - Gold Tier System
echo =====================================================
echo.
echo Starting all Gold tier components...
echo.

echo Creating required directories...
mkdir Inbox 2>nul
mkdir Needs_Action 2>nul
mkdir Plans 2>nul
mkdir Pending_Approval 2>nul
mkdir Approved 2>nul
mkdir Rejected 2>nul
mkdir Done 2>nul
mkdir Logs 2>nul
mkdir Briefings 2>nul
mkdir Updates 2>nul
mkdir Accounting 2>nul
mkdir Invoices 2>nul
mkdir RalphWiggumStates 2>nul

echo.
echo Starting Filesystem Watcher...
start "Filesystem Watcher" /min python filesystem_watcher.py

timeout /t 2 /nobreak >nul

echo Starting Gmail Watcher...
start "Gmail Watcher" /min python gmail_watcher.py

timeout /t 2 /nobreak >nul

echo Starting WhatsApp Watcher...
start "WhatsApp Watcher" /min python whatsapp_watcher.py

timeout /t 2 /nobreak >nul

echo Starting Expense Policy Enforcer...
start "Expense Policy Enforcer" /min python expense-policy-enforcer\expense_policy_enforcer.py

timeout /t 2 /nobreak >nul

echo Starting Scheduler...
start "Scheduler" /min python scheduler.py

timeout /t 2 /nobreak >nul

echo Starting Gold Tier Orchestrator...
start "Gold Orchestrator" /min python gold_tier_orchestrator.py

timeout /t 2 /nobreak >nul

echo Starting System Health Monitor...
start "Health Monitor" /min python monitor_system_health.py

echo.
echo =====================================================
echo All Gold Tier AI Employee components started!
echo.
echo Components running:
echo.  - Filesystem Watcher (monitors Inbox folder)
echo.  - Gmail Watcher (monitors for important emails)
echo.  - WhatsApp Watcher (monitors for important WhatsApp messages)
echo.  - Expense Policy Enforcer (monitors transactions)
echo.  - Scheduler (handles daily/weekly tasks)
echo.  - Gold Tier Orchestrator (coordinates all operations)
echo.  - System Health Monitor (monitors system health)
echo.
echo Gold Tier Features:
echo.  - Enhanced audit logging
echo.  - Multiple MCP servers (Email, Social Media, Browser)
echo.  - Ralph Wiggum persistence loops
echo.  - Cross-domain integration
echo.  - Error recovery and graceful degradation
echo.
echo Press any key to see the system status...
echo =====================================================
pause >nul

echo.
echo Checking system status...
echo.
dir /B *.log 2>nul
echo.
echo Check orchestrator.log, scheduler.log, and other log files for details.
echo.
pause
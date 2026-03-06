@echo off
echo =====================================================
echo     Personal AI Employee - Silver Tier System
echo =====================================================
echo.
echo Starting all Silver tier components...
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

echo Starting Final Silver Orchestrator...
start "Silver Orchestrator" /min python final_silver_orchestrator.py

echo.
echo =====================================================
echo All Silver Tier AI Employee components started!
echo.
echo Components running:
echo.  - Filesystem Watcher (monitors Inbox folder)
echo.  - Gmail Watcher (monitors for important emails)
echo.  - WhatsApp Watcher (monitors for important WhatsApp messages)
echo.  - Expense Policy Enforcer (monitors transactions)
echo.  - Scheduler (handles daily/weekly tasks)
echo.  - Final Orchestrator (coordinates all operations)
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
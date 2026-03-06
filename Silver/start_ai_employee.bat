@echo off
echo Starting Personal AI Employee System...
echo.

echo Setting up environment...
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
start /min python filesystem_watcher.py

echo Starting Gmail Watcher...
start /min python gmail_watcher.py

echo Starting WhatsApp Watcher...
start /min python whatsapp_watcher.py

echo Starting Orchestrator...
start /min python improved_orchestrator.py

echo.
echo All AI Employee components started successfully!
echo.
echo The following processes are now running:
echo. - Filesystem Watcher (monitors Inbox folder)
echo. - Gmail Watcher (monitors for important emails)
echo. - WhatsApp Watcher (monitors for important WhatsApp messages)
echo. - Orchestrator (processes actions and approvals)
echo.
echo Press any key to exit...
pause >nul
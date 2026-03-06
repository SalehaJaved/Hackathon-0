@echo off
echo =====================================================
echo     Personal AI Employee - Platinum Tier System
echo =====================================================
echo.
echo Starting all Platinum tier components...
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
mkdir In_Progress\CloudAgent 2>nul
mkdir In_Progress\LocalAgent 2>nul
mkdir Signals 2>nul

echo.
echo Initializing Vault Synchronization...
python sync_vault_config.py

echo.
echo Starting Cloud Agent (handles: email triage, draft replies, social drafts)...
start "Cloud Agent" /min python cloud_agent_orchestrator.py

timeout /t 2 /nobreak >nul

echo Starting Local Agent (handles: approvals, WhatsApp, payments, final actions)...
start "Local Agent" /min python local_agent_orchestrator.py

timeout /t 2 /nobreak >nul

echo Starting Filesystem Watcher...
start "Filesystem Watcher" /min python filesystem_watcher.py

timeout /t 2 /nobreak >nul

echo Starting Gmail Watcher (Cloud domain)...
start "Gmail Watcher" /min python gmail_watcher.py

timeout /t 2 /nobreak >nul

echo Starting WhatsApp Watcher (Local domain only)...
start "WhatsApp Watcher" /min python whatsapp_watcher.py

timeout /t 2 /nobreak >nul

echo Starting Expense Policy Enforcer...
start "Expense Policy Enforcer" /min python expense-policy-enforcer\expense_policy_enforcer.py

timeout /t 2 /nobreak >nul

echo Starting Scheduler...
start "Scheduler" /min python scheduler.py

timeout /t 2 /nobreak >nul

echo Starting Platinum Tier Orchestrator...
start "Platinum Orchestrator" /min python platinum_tier_orchestrator.py

timeout /t 2 /nobreak >nul

echo Starting System Health Monitor...
start "Health Monitor" /min python monitor_system_health.py

echo.
echo =====================================================
echo All Platinum Tier AI Employee components started!
echo.
echo Work-Zone Specialization Active:
echo  - Cloud Agent: Email triage, draft replies, social post drafts
echo  - Local Agent: Approvals, WhatsApp, payments, final actions
echo.
echo Components running:
echo.  - Cloud Agent Orchestrator
echo.  - Local Agent Orchestrator
echo.  - Filesystem Watcher
echo.  - Gmail Watcher (Cloud domain)
echo.  - WhatsApp Watcher (Local domain)
echo.  - Expense Policy Enforcer
echo.  - Scheduler
echo.  - Platinum Tier Orchestrator
echo.  - System Health Monitor
echo.
echo Vault Synchronization: Configured with security rules
echo Agent Coordination: Claim-by-move rule active
echo 24/7 Operation: Enabled with health monitoring
echo.
echo Press any key to see the system status...
echo =====================================================
pause >nul

echo.
echo Checking system status...
echo.
dir /B *.log 2>nul
echo.
echo Check platinum_orchestrator.log, cloud_agent.log, local_agent.log,
echo and other log files for details.
echo.
pause
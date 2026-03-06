"""
Platinum Tier Orchestrator for AI Employee
Coordinates Cloud and Local agents with 24/7 operation and domain specialization
"""
import os
import time
import logging
import json
import threading
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, Any, Optional


class PlatinumTierOrchestrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / 'platinum_orchestrator.log'),
                logging.StreamHandler()
            ]
        )

        # Initialize audit logger
        from audit_logger import AuditLogger
        self.audit_logger = AuditLogger(str(self.base_dir))

    def start_cloud_agent(self):
        """Start the cloud agent in a separate process"""
        try:
            # Start cloud agent
            cloud_process = subprocess.Popen([
                "python", "cloud_agent_orchestrator.py"
            ], cwd=str(self.base_dir))

            self.logger.info(f"Started Cloud Agent with PID: {cloud_process.pid}")

            self.audit_logger.log_action(
                action_type="agent_start",
                actor="platinum_orchestrator",
                target="cloud_agent",
                parameters={"pid": cloud_process.pid},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )

            return cloud_process

        except Exception as e:
            self.logger.error(f"Failed to start Cloud Agent: {e}")
            self.audit_logger.log_error(
                error_type="agent_start_error",
                error_message=str(e),
                context={"agent": "cloud_agent"},
                severity="high"
            )
            return None

    def start_local_agent(self):
        """Start the local agent in a separate process"""
        try:
            # Start local agent
            local_process = subprocess.Popen([
                "python", "local_agent_orchestrator.py"
            ], cwd=str(self.base_dir))

            self.logger.info(f"Started Local Agent with PID: {local_process.pid}")

            self.audit_logger.log_action(
                action_type="agent_start",
                actor="platinum_orchestrator",
                target="local_agent",
                parameters={"pid": local_process.pid},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )

            return local_process

        except Exception as e:
            self.logger.error(f"Failed to start Local Agent: {e}")
            self.audit_logger.log_error(
                error_type="agent_start_error",
                error_message=str(e),
                context={"agent": "local_agent"},
                severity="high"
            )
            return None

    def start_watchers(self):
        """Start the watcher processes for 24/7 operation"""
        import subprocess

        # Start Gmail watcher (cloud domain)
        try:
            subprocess.Popen(["python", "gmail_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started Gmail Watcher (Cloud domain)")
            self.audit_logger.log_action(
                action_type="process_start",
                actor="platinum_orchestrator",
                target="gmail_watcher",
                parameters={"type": "watcher", "domain": "cloud"},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )
        except Exception as e:
            self.logger.error(f"Failed to start Gmail Watcher: {e}")
            self.audit_logger.log_error(
                error_type="watcher_start_error",
                error_message=str(e),
                context={"watcher": "gmail", "domain": "cloud"},
                severity="high"
            )

        # Start Filesystem watcher (both domains)
        try:
            subprocess.Popen(["python", "filesystem_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started Filesystem Watcher (Cross-domain)")
            self.audit_logger.log_action(
                action_type="process_start",
                actor="platinum_orchestrator",
                target="filesystem_watcher",
                parameters={"type": "watcher", "domain": "cross"},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )
        except Exception as e:
            self.logger.error(f"Failed to start Filesystem Watcher: {e}")
            self.audit_logger.log_error(
                error_type="watcher_start_error",
                error_message=str(e),
                context={"watcher": "filesystem", "domain": "cross"},
                severity="high"
            )

        # Note: WhatsApp watcher is local-only due to session security
        # According to Platinum spec: "Local owns: WhatsApp session"
        self.logger.info("WhatsApp watcher will be managed by Local agent only")

    def run_health_monitoring(self):
        """Run 24/7 health monitoring for platinum system"""
        self.logger.info("Starting Platinum Tier Health Monitoring...")
        self.logger.info("Work-Zone Specialization Active:")
        self.logger.info("  - Cloud Agent: Email triage, draft replies, social post drafts")
        self.logger.info("  - Local Agent: Approvals, WhatsApp, payments, final actions")

        while True:
            try:
                # Check system health
                health_status = self.check_platinum_health()

                # Log system status
                self.logger.info(f"System health: {health_status['overall_status']}")

                # Log detailed status
                for component, status in health_status['components'].items():
                    if isinstance(status, dict) and 'status' in status:
                        self.logger.info(f"  - {component}: {status['status']}")
                    else:
                        self.logger.info(f"  - {component}: {status}")

                # Wait before next check
                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                self.logger.info("Platinum Tier Health Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in platinum health monitoring: {e}")
                self.audit_logger.log_error(
                    error_type="platinum_monitor_error",
                    error_message=str(e),
                    context={"component": "health_monitoring"},
                    severity="high"
                )
                time.sleep(60)  # Wait longer after error

    def check_platinum_health(self) -> Dict[str, Any]:
        """Check health of platinum-specific components"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {},
            "agents": {},
            "domains": {}
        }

        # Check if agent processes are running
        import psutil

        cloud_running = False
        local_running = False

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_info = proc.info
                proc_cmd = ' '.join(proc_info['cmdline']).lower() if proc_info['cmdline'] else ''

                if 'cloud_agent_orchestrator' in proc_cmd:
                    cloud_running = True
                if 'local_agent_orchestrator' in proc_cmd:
                    local_running = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        health_report["agents"]["cloud_agent"] = {"running": cloud_running, "status": "ok" if cloud_running else "not_running"}
        health_report["agents"]["local_agent"] = {"running": local_running, "status": "ok" if local_running else "not_running"}

        # Check domain-specific directories
        domain_dirs = ["Needs_Action", "Pending_Approval", "Approved", "Rejected", "Done",
                      "In_Progress/CloudAgent", "In_Progress/LocalAgent", "Updates", "Signals"]

        for dir_name in domain_dirs:
            dir_path = self.base_dir / dir_name
            exists = dir_path.exists()
            health_report["domains"][dir_name] = {"exists": exists, "status": "ok" if exists else "missing"}

            if not exists:
                health_report["overall_status"] = "degraded"

        # Check for platinum-specific functionality
        platinum_features = [
            ("cloud_agent_orchestrator.py", (self.base_dir / "cloud_agent_orchestrator.py").exists()),
            ("local_agent_orchestrator.py", (self.base_dir / "local_agent_orchestrator.py").exists()),
            ("In_Progress directory", (self.base_dir / "In_Progress").exists()),
            ("Updates directory", (self.base_dir / "Updates").exists()),
            ("Signals directory", (self.base_dir / "Signals").exists())
        ]

        for feature_name, exists in platinum_features:
            health_report["components"][feature_name] = {"exists": exists, "status": "ok" if exists else "missing"}
            if not exists:
                health_report["overall_status"] = "degraded"

        return health_report

    def run_platinum_demo(self):
        """Run the Platinum demo scenario: Email arrives while Local is offline →
        Cloud drafts reply + writes approval file → when Local returns, user approves →
        Local executes send via MCP → logs → moves task to /Done"""

        self.logger.info("Starting Platinum Demo Scenario...")
        self.logger.info("Simulating: Email arrives while Local is offline")

        # Create a simulated email arrival in Inbox (which gets processed by filesystem watcher)
        email_content = f"""---
type: email
from: client@example.com
subject: Urgent: Project Inquiry
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
Hello, I need urgent assistance with a project. Can you help?

## Suggested Actions
- [ ] Draft a reply
- [ ] Schedule a call
- [ ] Send proposal

## Additional Context
Client is interested in our services and needs quick response.
"""

        inbox_path = self.base_dir / "Inbox"
        inbox_path.mkdir(exist_ok=True)

        email_file = inbox_path / f"EMAIL_urgent_inquiry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(email_file, 'w', encoding='utf-8') as f:
            f.write(email_content)

        self.logger.info(f"Created simulated email: {email_file.name}")
        self.logger.info("Cloud agent should detect and process this email...")
        self.logger.info("Cloud will create draft reply in Pending_Approval")
        self.logger.info("Local agent will eventually approve and send")

    def main_loop(self):
        """Main loop for the platinum orchestrator"""
        self.logger.info("Starting Platinum Tier Orchestrator...")
        self.logger.info("Initializing 24/7 Cloud + Local Agent system with domain specialization")

        # Start agent processes
        cloud_agent = self.start_cloud_agent()
        local_agent = self.start_local_agent()

        # Start watchers for 24/7 operation
        self.start_watchers()

        # Run the platinum demo scenario
        self.run_platinum_demo()

        # Start health monitoring
        self.run_health_monitoring()


def main():
    orchestrator = PlatinumTierOrchestrator()
    orchestrator.main_loop()


if __name__ == "__main__":
    main()
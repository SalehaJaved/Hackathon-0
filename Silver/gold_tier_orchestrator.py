"""
Gold Tier Orchestrator for the Personal AI Employee Hackathon

This orchestrator includes all Silver tier features plus:
- Comprehensive error recovery and graceful degradation
- Multiple MCP server integration
- Advanced scheduling capabilities
- Enhanced audit logging
- Cross-domain integration capabilities
"""
import os
import time
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
import threading
import signal
import sys
from typing import List, Dict, Any, Optional
import sys
import os
# Add the expense-policy-enforcer directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'expense-policy-enforcer'))
from expense_policy_enforcer import ExpensePolicyEnforcer
from audit_logger import AuditLogger


class GoldTierOrchestrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logger = logging.getLogger(self.__class__.__name__)
        self.audit_logger = AuditLogger(str(self.base_dir))
        self.exit_flag = threading.Event()

        # MCP servers status tracking
        self.mcp_servers = {}

        # Initialize error tracking
        self.error_count = 0
        self.max_errors = 10

    def check_needs_action_folder(self):
        """Check if /Needs_Action folder contains any files"""
        needs_action_path = self.base_dir / "Needs_Action"

        if not needs_action_path.exists():
            self.logger.info("Needs_Action folder does not exist")
            needs_action_path.mkdir(exist_ok=True)  # Create if it doesn't exist
            return False

        # Check if folder contains any files
        files = list(needs_action_path.iterdir())
        return len(files) > 0

    def check_pending_approval_folder(self):
        """Check if /Pending_Approval folder contains any files"""
        pending_approval_path = self.base_dir / "Pending_Approval"

        if not pending_approval_path.exists():
            self.logger.info("Pending_Approval folder does not exist")
            pending_approval_path.mkdir(exist_ok=True)  # Create if it doesn't exist
            return False

        # Check if folder contains any files
        files = list(pending_approval_path.iterdir())
        return len(files) > 0

    def check_approved_folder(self):
        """Check if /Approved folder contains any files to process"""
        approved_path = self.base_dir / "Approved"

        if not approved_path.exists():
            return False

        # Check if folder contains any files
        files = list(approved_path.iterdir())
        return len(files) > 0

    def run_claude_command(self, command_type="process_needs_action", max_retries=3):
        """Execute the Claude CLI command to run the appropriate skill with error recovery"""
        for attempt in range(max_retries):
            try:
                if command_type == "process_needs_action":
                    cmd = ["claude", "Run process_needs_action skill"]
                elif command_type == "process_approval":
                    cmd = ["claude", "Run process_approval skill"]
                elif command_type == "business_audit":
                    cmd = ["claude", "Run business_audit skill"]
                else:
                    cmd = ["claude", "Run process_needs_action skill"]  # Default

                self.logger.info(f"Executing Claude command: {' '.join(cmd)}")

                # Log the action
                self.audit_logger.log_action(
                    action_type="claude_command",
                    actor="orchestrator",
                    target="claude_code",
                    parameters={"command": " ".join(cmd)},
                    approval_status="system_approved",
                    approved_by="orchestrator",
                    result="pending"
                )

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    cwd=str(self.base_dir)  # Run in the current directory
                )

                if result.returncode == 0:
                    self.logger.info(f"Successfully executed Claude command: {result.stdout}")
                    self.audit_logger.log_action(
                        action_type="claude_command",
                        actor="orchestrator",
                        target="claude_code",
                        parameters={"command": " ".join(cmd)},
                        approval_status="system_approved",
                        approved_by="orchestrator",
                        result="success"
                    )
                    return True
                else:
                    self.logger.error(f"Error executing Claude command: {result.stderr}")
                    self.audit_logger.log_action(
                        action_type="claude_command",
                        actor="orchestrator",
                        target="claude_code",
                        parameters={"command": " ".join(cmd)},
                        approval_status="system_approved",
                        approved_by="orchestrator",
                        result="failure",
                        additional_info={"error": result.stderr}
                    )
                    if attempt == max_retries - 1:  # Last attempt
                        return False
                    time.sleep(5)  # Wait before retry

            except subprocess.TimeoutExpired:
                self.logger.error(f"Claude command timed out after 10 minutes (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    return False
                time.sleep(5)
            except FileNotFoundError:
                self.logger.error("Claude CLI not found. Please ensure it's installed and in PATH")
                self.audit_logger.log_error(
                    error_type="claude_not_found",
                    error_message="Claude CLI not found",
                    context={"command_type": command_type},
                    severity="high"
                )
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error running Claude command (attempt {attempt + 1}): {str(e)}")
                self.audit_logger.log_error(
                    error_type="claude_command_error",
                    error_message=str(e),
                    context={"command_type": command_type, "attempt": attempt + 1},
                    severity="medium"
                )
                if attempt == max_retries - 1:
                    return False
                time.sleep(5)

        return False

    def process_approved_files(self):
        """Process files that have been moved to the /Approved folder"""
        approved_path = self.base_dir / "Approved"
        done_path = self.base_dir / "Done"

        if not approved_path.exists():
            return False

        # Check if folder contains any files
        files = list(approved_path.iterdir())
        if not files:
            return False

        self.logger.info(f"Found {len(files)} approved files to process")

        for file_path in files:
            if file_path.is_file():
                self.logger.info(f"Processing approved file: {file_path.name}")

                # Log the start of processing
                self.audit_logger.log_action(
                    action_type="file_processing",
                    actor="orchestrator",
                    target=str(file_path),
                    parameters={"folder": "Approved"},
                    approval_status="approved",
                    approved_by="human",
                    result="in_progress"
                )

                # Process the approved file based on its type
                try:
                    # Read the file to determine its type
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Process based on file type
                    if 'type: email_draft' in content or 'type: social_post_draft' in content:
                        # For email/social posts, trigger the appropriate MCP
                        success = self.execute_mcp_action(file_path, content)
                        if success:
                            # Move to Done folder
                            done_file_path = done_path / file_path.name
                            file_path.rename(done_file_path)
                            self.logger.info(f"Moved approved file to Done: {file_path.name}")

                            # Log successful completion
                            self.audit_logger.log_action(
                                action_type="file_processing",
                                actor="orchestrator",
                                target=str(done_file_path),
                                parameters={"folder": "Done", "original_folder": "Approved"},
                                approval_status="approved",
                                approved_by="human",
                                result="success"
                            )
                    elif 'type: scheduled_social_post' in content:
                        self.logger.info(f"Scheduled post approved: {file_path.name}")
                        success = self.execute_mcp_action(file_path, content)
                        if success:
                            done_file_path = done_path / file_path.name
                            file_path.rename(done_file_path)
                    elif 'type: linkedin_campaign' in content:
                        self.logger.info(f"LinkedIn campaign approved: {file_path.name}")
                        success = self.execute_mcp_action(file_path, content)
                        if success:
                            done_file_path = done_path / file_path.name
                            file_path.rename(done_file_path)
                    else:
                        # For unknown types, just move to Done
                        done_file_path = done_path / file_path.name
                        file_path.rename(done_file_path)
                        self.logger.info(f"Moved untyped approved file to Done: {file_path.name}")

                except Exception as e:
                    self.logger.error(f"Error processing approved file {file_path.name}: {e}")
                    self.audit_logger.log_error(
                        error_type="file_processing_error",
                        error_message=str(e),
                        context={"file_path": str(file_path), "folder": "Approved"},
                        severity="medium"
                    )
                    # Still move to done but log the error
                    done_file_path = done_path / f"ERROR_{file_path.name}"
                    file_path.rename(done_file_path)

        return True

    def execute_mcp_action(self, file_path: Path, content: str) -> bool:
        """Execute the appropriate MCP action based on file content"""
        try:
            # This is a placeholder - in a real implementation, you would call the appropriate MCP server
            # based on the content of the approved file

            self.logger.info(f"Executing MCP action for: {file_path.name}")

            # Log the MCP action attempt
            self.audit_logger.log_action(
                action_type="mcp_action_execute",
                actor="orchestrator",
                target=str(file_path.name),
                parameters={"content_preview": content[:200]},
                approval_status="approved",
                approved_by="human",
                result="executing"
            )

            # In a real implementation, this would:
            # 1. Parse the file content to determine the action
            # 2. Call the appropriate MCP server based on action type
            # 3. Handle the result and potential errors

            # For now, we'll simulate successful execution
            self.logger.info(f"MCP action simulated for: {file_path.name}")

            # Log successful execution
            self.audit_logger.log_action(
                action_type="mcp_action_execute",
                actor="orchestrator",
                target=str(file_path.name),
                parameters={"content_preview": content[:200]},
                approval_status="approved",
                approved_by="human",
                result="success"
            )

            return True

        except Exception as e:
            self.logger.error(f"Error executing MCP action for {file_path.name}: {e}")
            self.audit_logger.log_error(
                error_type="mcp_execution_error",
                error_message=str(e),
                context={"file_path": str(file_path), "content_preview": content[:200]},
                severity="high"
            )
            return False

    def run_business_audit_if_needed(self):
        """Run the weekly business audit if it's time"""
        # Check if it's Sunday evening for the weekly audit
        current_time = datetime.now()
        if current_time.weekday() == 6 and current_time.hour >= 19:  # Sunday, after 7 PM
            self.logger.info("Running weekly business audit...")
            try:
                # Execute Claude to perform the audit
                cmd = ["python", "business_briefing_generator.py"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(self.base_dir)
                )

                if result.returncode == 0:
                    self.logger.info("Business audit completed successfully")
                    self.audit_logger.log_action(
                        action_type="business_audit",
                        actor="orchestrator",
                        target="business_briefing_generator",
                        parameters={"type": "weekly"},
                        approval_status="system_approved",
                        approved_by="system",
                        result="success"
                    )
                else:
                    self.logger.error(f"Business audit failed: {result.stderr}")
                    self.audit_logger.log_action(
                        action_type="business_audit",
                        actor="orchestrator",
                        target="business_briefing_generator",
                        parameters={"type": "weekly"},
                        approval_status="system_approved",
                        approved_by="system",
                        result="failure",
                        additional_info={"error": result.stderr}
                    )
            except Exception as e:
                self.logger.error(f"Error running business audit: {e}")
                self.audit_logger.log_error(
                    error_type="business_audit_error",
                    error_message=str(e),
                    context={"type": "weekly"},
                    severity="high"
                )

    def run_expense_policy_check(self):
        """Run the expense policy enforcer"""
        try:
            enforcer = ExpensePolicyEnforcer(str(self.base_dir))
            enforcer.run_policy_check()

            self.audit_logger.log_action(
                action_type="expense_policy_check",
                actor="orchestrator",
                target="expense_policy_enforcer",
                parameters={},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )
        except Exception as e:
            self.logger.error(f"Error running expense policy check: {e}")
            self.audit_logger.log_error(
                error_type="expense_policy_error",
                error_message=str(e),
                context={"component": "expense_policy_enforcer"},
                severity="high"
            )

    def run_daily_tasks(self):
        """Run daily maintenance tasks"""
        current_time = datetime.now()

        # Run expense policy check daily at 6 AM
        if current_time.hour == 6 and current_time.minute < 5:
            self.run_expense_policy_check()

        # Check for accounting tasks (Gold Tier requirement)
        self.run_accounting_integration()

        # Run business audit if needed
        self.run_business_audit_if_needed()

    def run_accounting_integration(self):
        """Run accounting system integration (Gold Tier requirement)"""
        # This is where you'd integrate with an accounting system like Odoo
        # For now, we'll implement a basic accounting audit
        self.logger.info("Running accounting integration check...")

        try:
            # Check Accounting folder for new entries
            accounting_dir = self.base_dir / "Accounting"
            if accounting_dir.exists():
                # Process any new accounting files
                for file_path in accounting_dir.glob("*.json"):
                    self.process_accounting_file(file_path)

            self.audit_logger.log_action(
                action_type="accounting_integration",
                actor="orchestrator",
                target="accounting_system",
                parameters={"integration_type": "file_based"},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )

        except Exception as e:
            self.logger.error(f"Error in accounting integration: {e}")
            self.audit_logger.log_error(
                error_type="accounting_integration_error",
                error_message=str(e),
                context={"component": "accounting_system"},
                severity="high"
            )

    def process_accounting_file(self, file_path: Path):
        """Process an accounting file for integration"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # In a real implementation, this would integrate with an accounting system
            # For now, we'll just log what we found
            self.logger.info(f"Processing accounting file: {file_path.name}")

        except Exception as e:
            self.logger.error(f"Error processing accounting file {file_path.name}: {e}")
            self.audit_logger.log_error(
                error_type="accounting_file_error",
                error_message=str(e),
                context={"file_path": str(file_path)},
                severity="medium"
            )

    def start_watchers(self):
        """Start the watcher processes in separate threads"""
        import subprocess

        # Start Gmail watcher
        try:
            subprocess.Popen(["python", "gmail_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started Gmail Watcher")
            self.audit_logger.log_action(
                action_type="process_start",
                actor="orchestrator",
                target="gmail_watcher",
                parameters={"type": "watcher"},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )
        except Exception as e:
            self.logger.error(f"Failed to start Gmail Watcher: {e}")
            self.audit_logger.log_error(
                error_type="watcher_start_error",
                error_message=str(e),
                context={"watcher": "gmail"},
                severity="high"
            )

        # Start WhatsApp watcher
        try:
            subprocess.Popen(["python", "whatsapp_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started WhatsApp Watcher")
            self.audit_logger.log_action(
                action_type="process_start",
                actor="orchestrator",
                target="whatsapp_watcher",
                parameters={"type": "watcher"},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )
        except Exception as e:
            self.logger.error(f"Failed to start WhatsApp Watcher: {e}")
            self.audit_logger.log_error(
                error_type="watcher_start_error",
                error_message=str(e),
                context={"watcher": "whatsapp"},
                severity="high"
            )

        # Start Filesystem watcher
        try:
            subprocess.Popen(["python", "filesystem_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started Filesystem Watcher")
            self.audit_logger.log_action(
                action_type="process_start",
                actor="orchestrator",
                target="filesystem_watcher",
                parameters={"type": "watcher"},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )
        except Exception as e:
            self.logger.error(f"Failed to start Filesystem Watcher: {e}")
            self.audit_logger.log_error(
                error_type="watcher_start_error",
                error_message=str(e),
                context={"watcher": "filesystem"},
                severity="high"
            )

    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        import subprocess

        try:
            subprocess.Popen(["python", "scheduler.py"], cwd=str(self.base_dir))
            self.logger.info("Started Scheduler")
            self.audit_logger.log_action(
                action_type="process_start",
                actor="orchestrator",
                target="scheduler",
                parameters={"type": "scheduler"},
                approval_status="system_approved",
                approved_by="system",
                result="success"
            )
        except Exception as e:
            self.logger.error(f"Failed to start Scheduler: {e}")
            self.audit_logger.log_error(
                error_type="scheduler_start_error",
                error_message=str(e),
                context={"component": "scheduler"},
                severity="high"
            )

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.exit_flag.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def main_loop(self):
        """Main orchestration loop with error recovery"""
        self.logger.info("Starting Gold Tier Orchestrator...")
        self.audit_logger.log_action(
            action_type="orchestrator_start",
            actor="system",
            target="gold_tier_orchestrator",
            parameters={},
            approval_status="system_approved",
            approved_by="system",
            result="success"
        )

        # Setup graceful shutdown
        self.setup_signal_handlers()

        # Start watchers and scheduler
        self.start_watchers()
        self.start_scheduler()

        while not self.exit_flag.is_set():
            try:
                # Check for needs action files
                if self.check_needs_action_folder():
                    self.logger.info("Found files in Needs_Action folder, triggering Claude command")
                    if not self.run_claude_command("process_needs_action"):
                        self.logger.error("Failed to process Needs_Action files after retries")
                        self.error_count += 1
                        if self.error_count >= self.max_errors:
                            self.logger.error("Too many errors, initiating graceful shutdown")
                            break

                # Check for pending approval files
                if self.check_pending_approval_folder():
                    self.logger.info("Found files in Pending_Approval folder, triggering Claude approval processing")
                    if not self.run_claude_command("process_approval"):
                        self.logger.error("Failed to process Pending_Approval files after retries")
                        self.error_count += 1
                        if self.error_count >= self.max_errors:
                            self.logger.error("Too many errors, initiating graceful shutdown")
                            break

                # Process any approved files
                self.process_approved_files()

                # Run daily tasks
                self.run_daily_tasks()

                # Wait for 60 seconds before next check
                # Use a more sophisticated wait that can be interrupted
                for _ in range(60):
                    if self.exit_flag.is_set():
                        break
                    time.sleep(1)

            except KeyboardInterrupt:
                self.logger.info("Orchestrator stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in orchestrator loop: {str(e)}")
                self.audit_logger.log_error(
                    error_type="orchestrator_loop_error",
                    error_message=str(e),
                    context={"component": "main_loop"},
                    severity="high"
                )

                # Increment error counter
                self.error_count += 1
                if self.error_count >= self.max_errors:
                    self.logger.error("Too many errors, initiating graceful shutdown")
                    break

                # Continue the loop even if there's an error, but wait before retrying
                time.sleep(60)

        # Log shutdown
        self.logger.info("Gold Tier Orchestrator shutting down...")
        self.audit_logger.log_action(
            action_type="orchestrator_shutdown",
            actor="system",
            target="gold_tier_orchestrator",
            parameters={"error_count": self.error_count},
            approval_status="system_approved",
            approved_by="system",
            result="success"
        )

    def run_health_check(self):
        """Run a comprehensive health check of the system"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall_status": "healthy"
        }

        # Check if key directories exist
        dirs_to_check = [
            "Inbox", "Needs_Action", "Plans", "Pending_Approval",
            "Approved", "Rejected", "Done", "Logs", "Briefings"
        ]

        for dir_name in dirs_to_check:
            dir_path = self.base_dir / dir_name
            exists = dir_path.exists()
            health_report["components"][dir_name] = {
                "exists": exists,
                "status": "ok" if exists else "missing"
            }
            if not exists:
                health_report["overall_status"] = "degraded"

        # Check key files
        files_to_check = [
            "final_silver_orchestrator.py",
            "gmail_watcher.py",
            "whatsapp_watcher.py",
            "business_briefing_generator.py",
            "scheduler.py"
        ]

        for file_name in files_to_check:
            file_path = self.base_dir / file_name
            exists = file_path.exists()
            health_report["components"][file_name] = {
                "exists": exists,
                "status": "ok" if exists else "missing"
            }
            if not exists:
                health_report["overall_status"] = "degraded"

        # Log the health check
        self.audit_logger.log_action(
            action_type="health_check",
            actor="orchestrator",
            target="system_health",
            parameters={"report": health_report},
            approval_status="system_approved",
            approved_by="system",
            result="completed"
        )

        return health_report


def main():
    orchestrator = GoldTierOrchestrator()

    # Run health check first
    health = orchestrator.run_health_check()
    print(f"System health: {health['overall_status']}")

    # Run one cycle of the orchestrator (like in Silver)
    # Only run main loop if we want continuous operation
    # For testing purposes, let's run one cycle like the Silver version
    orchestrator.run_daily_tasks()  # Run daily tasks like checking for new files

    # Process any files that need action
    if orchestrator.check_needs_action_folder():
        orchestrator.logger.info("Found files in Needs_Action folder, triggering Claude command")
        orchestrator.run_claude_command("process_needs_action")

    # Check for pending approval files
    if orchestrator.check_pending_approval_folder():
        orchestrator.logger.info("Found files in Pending_Approval folder, triggering Claude approval processing")
        orchestrator.run_claude_command("process_approval")

    # Process any approved files
    orchestrator.process_approved_files()


if __name__ == "__main__":
    main()
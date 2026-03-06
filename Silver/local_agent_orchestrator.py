"""
Local Agent Orchestrator for Platinum Tier AI Employee
Handles local-specific tasks: approvals, WhatsApp, payments, final actions
"""
import os
import time
import logging
import json
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, Any, Optional


class LocalAgentOrchestrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / 'local_agent.log'),
                logging.StreamHandler()
            ]
        )

        # Agent-specific directories
        self.in_progress_local = self.base_dir / "In_Progress" / "LocalAgent"
        self.in_progress_local.mkdir(parents=True, exist_ok=True)

        self.updates_dir = self.base_dir / "Updates"
        self.updates_dir.mkdir(exist_ok=True)

        self.signals_dir = self.base_dir / "Signals"
        self.signals_dir.mkdir(exist_ok=True)

    def claim_task(self, source_file_path: Path, task_type: str) -> Optional[Path]:
        """Claim a task using the 'claim-by-move' rule"""
        try:
            # Create unique filename for this agent
            task_id = f"{task_type}_{source_file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
            claimed_file = self.in_progress_local / f"{task_id}.md"

            # Move the task to the LocalAgent's In_Progress folder
            source_file_path.rename(claimed_file)

            self.logger.info(f"Local agent claimed task: {source_file_path.name} -> {claimed_file.name}")
            return claimed_file

        except Exception as e:
            self.logger.error(f"Failed to claim task {source_file_path}: {e}")
            return None

    def process_pending_approval_folder(self):
        """Process files in /Pending_Approval folder (local's domain)"""
        pending_approval_path = self.base_dir / "Pending_Approval"

        if not pending_approval_path.exists():
            return False

        # Check if folder contains any files
        files = list(pending_approval_path.iterdir())

        for file_path in files:
            if file_path.is_file():
                claimed_task = self.claim_task(file_path, "approval_processing")
                if claimed_task:
                    self.execute_approved_action(claimed_task)

        return True

    def execute_approved_action(self, task_file: Path):
        """Execute actions that require local control: payments, WhatsApp, sending emails/social posts"""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine action type based on content
            if 'type: email_draft' in content.lower():
                self.execute_email_send(task_file, content)
            elif 'type: social_post_draft' in content.lower():
                self.execute_social_post(task_file, content)
            elif 'type: payment' in content.lower() or 'payment' in content.lower():
                self.execute_payment(task_file, content)
            else:
                # Move to Done as default
                self.move_to_done(task_file, "unknown_action_type")

        except Exception as e:
            self.logger.error(f"Error executing approved action {task_file}: {e}")
            self.move_to_done(task_file, "error")

    def execute_email_send(self, task_file: Path, content: str):
        """Execute email sending via MCP (local has credentials)"""
        self.logger.info(f"Local agent executing email send for: {task_file.name}")

        # This is where the Local agent would call the email MCP server
        # Since we don't have actual credentials, we'll simulate the action
        self.logger.info(f"Email draft approved for sending: {task_file.name}")

        # In a real implementation, this would call:
        # result = self.call_mcp_tool("send_email", email_params)

        # Move to Done
        self.move_to_done(task_file, "email_sent_simulation")

    def execute_social_post(self, task_file: Path, content: str):
        """Execute social media posting via MCP (local has credentials)"""
        self.logger.info(f"Local agent executing social post for: {task_file.name}")

        # This is where the Local agent would call the social media MCP server
        self.logger.info(f"Social post approved for publishing: {task_file.name}")

        # In a real implementation, this would call:
        # result = self.call_mcp_tool("post_social_media", social_params)

        # Move to Done
        self.move_to_done(task_file, "social_posted_simulation")

    def execute_payment(self, task_file: Path, content: str):
        """Execute payment actions (local has banking credentials)"""
        self.logger.info(f"Local agent executing payment for: {task_file.name}")

        # This is where the Local agent would execute actual payment
        self.logger.info(f"Payment approved and processed: {task_file.name}")

        # Move to Done
        self.move_to_done(task_file, "payment_processed_simulation")

    def move_to_done(self, task_file: Path, action_result: str):
        """Move task file to Done folder with proper naming"""
        done_path = self.base_dir / "Done"
        done_path.mkdir(exist_ok=True)

        new_name = f"DONE_{task_file.stem}_{action_result.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        final_path = done_path / new_name

        with open(task_file, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Add execution result to content
        updated_content = f"""{original_content}

---
execution_result: {action_result}
executed_by: local_agent
execution_time: {datetime.now().isoformat()}
---

# Execution Log
- Action completed by Local Agent
- Result: {action_result}
- Time: {datetime.now().isoformat()}
"""

        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        # Remove the original claimed task file
        task_file.unlink()

        self.logger.info(f"Task moved to Done: {final_path.name}")

    def merge_updates_to_dashboard(self):
        """Merge updates from cloud agent into Dashboard.md (single-writer rule)"""
        # Process any update files in the Updates directory
        if not self.updates_dir.exists():
            return

        update_files = list(self.updates_dir.glob("*.md"))
        if not update_files:
            return

        # Merge updates into Dashboard.md
        dashboard_path = self.base_dir / "Dashboard.md"

        # Read existing dashboard
        if dashboard_path.exists():
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
        else:
            dashboard_content = "# Dashboard\n\n## Recent Activity\n"

        # Add updates to dashboard
        for update_file in update_files:
            try:
                with open(update_file, 'r', encoding='utf-8') as f:
                    update_content = f.read()

                # Add update to dashboard
                update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                dashboard_content += f"- [{update_time}] Cloud Agent Update: {update_file.stem}\n"

                # Delete processed update file
                update_file.unlink()

            except Exception as e:
                self.logger.error(f"Error processing update file {update_file}: {e}")

        # Write updated dashboard
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

        self.logger.info(f"Merged {len(update_files)} updates into Dashboard.md")

    def process_signals(self):
        """Process signals from cloud agent"""
        if not self.signals_dir.exists():
            return

        signal_files = list(self.signals_dir.glob("*.md"))
        for signal_file in signal_files:
            try:
                with open(signal_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.logger.info(f"Processing signal from cloud: {signal_file.name}")
                self.logger.info(f"Signal content: {content[:200]}...")

                # Process the signal as needed
                # For now, just log it and move to updates
                self.move_signal_to_updates(signal_file)

            except Exception as e:
                self.logger.error(f"Error processing signal {signal_file}: {e}")

    def move_signal_to_updates(self, signal_file: Path):
        """Move processed signal to updates"""
        update_path = self.updates_dir / f"PROCESSED_{signal_file.name}"
        signal_file.rename(update_path)

    def run_health_monitoring(self):
        """Run health monitoring for local agent"""
        self.logger.info("Starting Local Agent Health Monitoring...")

        while True:
            try:
                # Check system health
                self.check_local_health()

                # Process pending approvals (local's domain)
                self.process_pending_approval_folder()

                # Merge updates from cloud agent to Dashboard (single-writer rule)
                self.merge_updates_to_dashboard()

                # Process any signals from cloud agent
                self.process_signals()

                # Wait before next check
                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                self.logger.info("Local Agent Health Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                time.sleep(60)  # Wait longer after error

    def check_local_health(self):
        """Check health of local-specific components"""
        # This would include checking local-specific services like WhatsApp session
        # For now, just log that we're running
        self.logger.info("Local agent health check: operational")

    def main_loop(self):
        """Main loop for the local agent"""
        self.logger.info("Starting Local Agent Orchestrator...")
        self.logger.info("Local Agent specializes in: approvals, WhatsApp, payments, final actions")
        self.logger.info("Cloud Agent handles: email triage, draft replies, social post drafts")

        # Start the health monitoring
        self.run_health_monitoring()


def main():
    orchestrator = LocalAgentOrchestrator()
    orchestrator.main_loop()


if __name__ == "__main__":
    main()
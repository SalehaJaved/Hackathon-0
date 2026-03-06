"""
Final Silver Tier Orchestrator for the Personal AI Employee Hackathon

This orchestrator integrates all Silver tier features:
- Multiple watchers (filesystem, Gmail, WhatsApp)
- MCP server integration
- Human-in-the-loop approval workflow
- Business audit capabilities
- Expense policy enforcement
- Scheduling system
"""

import os
import time
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
import threading
import sys
import os
# Add the expense-policy-enforcer directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'expense-policy-enforcer'))
from expense_policy_enforcer import ExpensePolicyEnforcer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)


class SilverTierOrchestrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_needs_action_folder(self):
        """Check if /Needs_Action folder contains any files"""
        needs_action_path = self.base_dir / "Needs_Action"

        if not needs_action_path.exists():
            logging.info("Needs_Action folder does not exist")
            needs_action_path.mkdir(exist_ok=True)  # Create if it doesn't exist
            return False

        # Check if folder contains any files
        files = list(needs_action_path.iterdir())
        return len(files) > 0

    def check_pending_approval_folder(self):
        """Check if /Pending_Approval folder contains any files"""
        pending_approval_path = self.base_dir / "Pending_Approval"

        if not pending_approval_path.exists():
            logging.info("Pending_Approval folder does not exist")
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

    def run_claude_command(self, command_type="process_needs_action"):
        """Execute the Claude CLI command to run the appropriate skill"""
        try:
            if command_type == "process_needs_action":
                cmd = ["claude", "Run process_needs_action skill"]
            elif command_type == "process_approval":
                cmd = ["claude", "Run process_approval skill"]
            else:
                cmd = ["claude", "Run process_needs_action skill"]  # Default

            logging.info(f"Executing Claude command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=str(self.base_dir)  # Run in the current directory
            )

            if result.returncode == 0:
                logging.info(f"Successfully executed Claude command: {result.stdout}")
                return True
            else:
                logging.error(f"Error executing Claude command: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logging.error("Claude command timed out after 10 minutes")
            return False
        except FileNotFoundError:
            logging.warning("Claude CLI not found. Please ensure it's installed and in PATH")
            return False
        except Exception as e:
            logging.error(f"Unexpected error running Claude command: {str(e)}")
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

        logging.info(f"Found {len(files)} approved files to process")

        for file_path in files:
            if file_path.is_file():
                logging.info(f"Processing approved file: {file_path.name}")

                # Process the approved file based on its type
                try:
                    # Read the file to determine its type
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Process based on file type
                    if 'type: email_draft' in content or 'type: social_post_draft' in content:
                        # For email/social posts, this would trigger the MCP to execute
                        logging.info(f"Ready to execute action for: {file_path.name}")
                        # In a real implementation, this would call the appropriate MCP
                    elif 'type: scheduled_social_post' in content:
                        logging.info(f"Scheduled post approved: {file_path.name}")
                    elif 'type: linkedin_campaign' in content:
                        logging.info(f"LinkedIn campaign approved: {file_path.name}")

                    # Move to Done folder
                    done_file_path = done_path / file_path.name
                    file_path.rename(done_file_path)
                    logging.info(f"Moved approved file to Done: {file_path.name}")
                except Exception as e:
                    logging.error(f"Error processing approved file {file_path.name}: {e}")

        return True

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
                else:
                    self.logger.error(f"Business audit failed: {result.stderr}")
            except Exception as e:
                self.logger.error(f"Error running business audit: {e}")

    def run_expense_policy_check(self):
        """Run the expense policy enforcer"""
        try:
            enforcer = ExpensePolicyEnforcer(str(self.base_dir))
            enforcer.run_policy_check()
        except Exception as e:
            self.logger.error(f"Error running expense policy check: {e}")

    def run_daily_tasks(self):
        """Run daily maintenance tasks"""
        current_time = datetime.now()

        # Run expense policy check daily at 6 AM
        if current_time.hour == 6 and current_time.minute < 5:
            self.run_expense_policy_check()

        # Run business audit if needed
        self.run_business_audit_if_needed()

    def start_watchers(self):
        """Start the watcher processes in separate threads"""
        import subprocess

        # Start Gmail watcher
        try:
            subprocess.Popen(["python", "gmail_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started Gmail Watcher")
        except Exception as e:
            self.logger.error(f"Failed to start Gmail Watcher: {e}")

        # Start WhatsApp watcher
        try:
            subprocess.Popen(["python", "whatsapp_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started WhatsApp Watcher")
        except Exception as e:
            self.logger.error(f"Failed to start WhatsApp Watcher: {e}")

        # Start Filesystem watcher
        try:
            subprocess.Popen(["python", "filesystem_watcher.py"], cwd=str(self.base_dir))
            self.logger.info("Started Filesystem Watcher")
        except Exception as e:
            self.logger.error(f"Failed to start Filesystem Watcher: {e}")

    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        import subprocess

        try:
            subprocess.Popen(["python", "scheduler.py"], cwd=str(self.base_dir))
            self.logger.info("Started Scheduler")
        except Exception as e:
            self.logger.error(f"Failed to start Scheduler: {e}")

    def main_loop(self):
        """Main orchestration loop"""
        self.logger.info("Starting Silver Tier Orchestrator...")

        # Start watchers and scheduler
        self.start_watchers()
        self.start_scheduler()

        while True:
            try:
                # Check for needs action files
                if self.check_needs_action_folder():
                    self.logger.info("Found files in Needs_Action folder, triggering Claude command")
                    self.run_claude_command("process_needs_action")

                # Check for pending approval files
                if self.check_pending_approval_folder():
                    self.logger.info("Found files in Pending_Approval folder, triggering Claude approval processing")
                    self.run_claude_command("process_approval")

                # Process any approved files
                self.process_approved_files()

                # Run daily tasks
                self.run_daily_tasks()

                # Wait for 60 seconds before next check
                time.sleep(60)

            except KeyboardInterrupt:
                self.logger.info("Orchestrator stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in orchestrator loop: {str(e)}")
                # Continue the loop even if there's an error
                time.sleep(60)

    def run_once(self):
        """Run one cycle of the orchestrator without the infinite loop"""
        self.logger.info("Running one cycle of Silver Tier Orchestrator...")

        # Check for needs action files
        if self.check_needs_action_folder():
            self.logger.info("Found files in Needs_Action folder, triggering Claude command")
            self.run_claude_command("process_needs_action")

        # Check for pending approval files
        if self.check_pending_approval_folder():
            self.logger.info("Found files in Pending_Approval folder, triggering Claude approval processing")
            self.run_claude_command("process_approval")

        # Process any approved files
        self.process_approved_files()

        # Run daily tasks
        self.run_daily_tasks()


def main():
    orchestrator = SilverTierOrchestrator()

    # Run one cycle of the orchestrator
    orchestrator.run_once()


if __name__ == "__main__":
    main()
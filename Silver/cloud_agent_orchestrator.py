"""
Cloud Agent Orchestrator for Platinum Tier AI Employee
Handles cloud-specific tasks: email triage, draft replies, social post drafts
"""
import os
import time
import logging
import json
from pathlib import Path
from datetime import datetime
import threading
from typing import Dict, Any, Optional


class CloudAgentOrchestrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / 'cloud_agent.log'),
                logging.StreamHandler()
            ]
        )

        # Agent-specific directories
        self.in_progress_cloud = self.base_dir / "In_Progress" / "CloudAgent"
        self.in_progress_cloud.mkdir(parents=True, exist_ok=True)

        self.updates_dir = self.base_dir / "Updates"
        self.updates_dir.mkdir(exist_ok=True)

        self.signals_dir = self.base_dir / "Signals"
        self.signals_dir.mkdir(exist_ok=True)

    def claim_task(self, source_file_path: Path, task_type: str) -> Optional[Path]:
        """Claim a task using the 'claim-by-move' rule"""
        try:
            # Create unique filename for this agent
            task_id = f"{task_type}_{source_file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
            claimed_file = self.in_progress_cloud / f"{task_id}.md"

            # Move the task to the CloudAgent's In_Progress folder
            source_file_path.rename(claimed_file)

            self.logger.info(f"Cloud agent claimed task: {source_file_path.name} -> {claimed_file.name}")
            return claimed_file

        except Exception as e:
            self.logger.error(f"Failed to claim task {source_file_path}: {e}")
            return None

    def process_needs_action_folder(self):
        """Process files in /Needs_Action folder, but with domain specialization"""
        needs_action_path = self.base_dir / "Needs_Action"

        if not needs_action_path.exists():
            return False

        # Check if folder contains any files
        files = list(needs_action_path.iterdir())

        for file_path in files:
            if file_path.is_file():
                # Specialize by domain - cloud handles email and social media drafts
                if 'EMAIL_' in file_path.name or 'GMAIL_' in file_path.name:
                    claimed_task = self.claim_task(file_path, "email_triage")
                    if claimed_task:
                        self.process_email_triage(claimed_task)
                elif 'WHATSAPP_' in file_path.name:
                    # According to platinum spec, WhatsApp is local-only, so cloud just observes
                    self.logger.info(f"Cloud: Not processing WhatsApp task {file_path.name} (local domain)")
                    # But we can create an update signal for local
                    self.create_update_signal(file_path, "whatsapp_task_detected")
                elif 'SOCIAL_POST' in file_path.name or 'LINKEDIN' in file_path.name:
                    claimed_task = self.claim_task(file_path, "social_draft")
                    if claimed_task:
                        self.process_social_draft(claimed_task)

        return True

    def process_email_triage(self, task_file: Path):
        """Process email triage and create draft replies requiring local approval"""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract email details from the task
            import re
            from_match = re.search(r'from: (.+)', content)
            subject_match = re.search(r'subject: (.+)', content)

            sender = from_match.group(1) if from_match else "Unknown"
            subject = subject_match.group(1) if subject_match else "No Subject"

            # Create a draft reply (cloud does draft, local does send)
            draft_content = f"""---
type: email_draft
created_by: cloud_agent
original_task: {task_file.name}
status: pending_approval
requires_local_action: true
---

# Email Draft Reply

**To:** {sender}
**Subject:** Re: {subject}

Dear {sender.split()[0] if sender != 'Unknown' else 'Sender'},

Thank you for your message. This is an automated reply from the AI Employee system.

This email has been processed by the cloud agent. The draft has been prepared and requires local approval before sending.

**Original message:**
{content[:500]}...  # Truncated original message

## Instructions
This email draft requires local approval. Move to /Approved folder to send, or /Rejected folder to discard.
"""

            # Save draft to Pending_Approval for local agent
            pending_approval_path = self.base_dir / "Pending_Approval"
            pending_approval_path.mkdir(exist_ok=True)

            draft_filename = f"CLOUD_DRAFT_{task_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            draft_path = pending_approval_path / draft_filename

            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)

            self.logger.info(f"Cloud agent created email draft for approval: {draft_path.name}")

            # Move completed task to Done
            done_path = self.base_dir / "Done"
            done_path.mkdir(exist_ok=True)
            final_done_path = done_path / f"COMPLETED_{task_file.name}"
            task_file.rename(final_done_path)

        except Exception as e:
            self.logger.error(f"Error processing email triage {task_file}: {e}")

    def process_social_draft(self, task_file: Path):
        """Process social media content and create draft posts requiring local approval"""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create a social media draft (cloud does draft, local does post)
            draft_content = f"""---
type: social_post_draft
platform: auto_detect
created_by: cloud_agent
original_task: {task_file.name}
status: pending_approval
requires_local_action: true
---

# Social Media Post Draft

**Platform:** [Auto-detected based on content]
**Content:**

{content}

## Instructions
This social media post draft requires local approval. Move to /Approved folder to post, or /Rejected folder to discard.
"""

            # Save draft to Pending_Approval for local agent
            pending_approval_path = self.base_dir / "Pending_Approval"
            draft_filename = f"CLOUD_SOCIAL_DRAFT_{task_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            draft_path = pending_approval_path / draft_filename

            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)

            self.logger.info(f"Cloud agent created social post draft for approval: {draft_path.name}")

            # Move completed task to Done
            done_path = self.base_dir / "Done"
            final_done_path = done_path / f"COMPLETED_{task_file.name}"
            task_file.rename(final_done_path)

        except Exception as e:
            self.logger.error(f"Error processing social draft {task_file}: {e}")

    def create_update_signal(self, original_file: Path, signal_type: str):
        """Create an update signal for the local agent"""
        signal_content = f"""---
signal_type: {signal_type}
timestamp: {datetime.now().isoformat()}
original_file: {original_file.name}
source_agent: cloud
---

# Update Signal

**Signal Type:** {signal_type}
**Original File:** {original_file.name}
**Time:** {datetime.now().isoformat()}

The cloud agent detected and logged this event for local processing.
"""

        signal_filename = f"SIGNAL_{signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        signal_path = self.signals_dir / signal_filename

        with open(signal_path, 'w', encoding='utf-8') as f:
            f.write(signal_content)

        self.logger.info(f"Created update signal: {signal_path.name}")

    def run_health_monitoring(self):
        """Run 24/7 health monitoring specific to cloud agent"""
        self.logger.info("Starting Cloud Agent Health Monitoring...")

        while True:
            try:
                # Check system health
                self.check_cloud_health()

                # Process any tasks in Needs_Action folder
                self.process_needs_action_folder()

                # Wait before next check
                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                self.logger.info("Cloud Agent Health Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                time.sleep(60)  # Wait longer after error

    def check_cloud_health(self):
        """Check health of cloud-specific components"""
        # This would include checking cloud-specific services
        # For now, just log that we're running
        self.logger.info("Cloud agent health check: operational")

    def main_loop(self):
        """Main loop for the cloud agent"""
        self.logger.info("Starting Cloud Agent Orchestrator...")
        self.logger.info("Cloud Agent specializes in: email triage, draft replies, social post drafts")
        self.logger.info("Local Agent handles: approvals, WhatsApp, payments, final actions")

        # Start the health monitoring
        self.run_health_monitoring()


def main():
    orchestrator = CloudAgentOrchestrator()
    orchestrator.main_loop()


if __name__ == "__main__":
    main()
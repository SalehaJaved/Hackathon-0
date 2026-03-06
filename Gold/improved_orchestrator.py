"""
Improved Orchestrator for the Personal AI Employee Hackathon

This orchestrator manages the workflow between watchers, Claude reasoning,
and external actions, including human-in-the-loop approval processes.
"""

import os
import time
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)


def check_needs_action_folder():
    """Check if /Needs_Action folder contains any files"""
    base_dir = Path(__file__).parent
    needs_action_path = base_dir / "Needs_Action"

    if not needs_action_path.exists():
        logging.warning("Needs_Action folder does not exist")
        needs_action_path.mkdir(exist_ok=True)  # Create if it doesn't exist
        return False

    # Check if folder contains any files
    files = list(needs_action_path.iterdir())
    return len(files) > 0


def check_pending_approval_folder():
    """Check if /Pending_Approval folder contains any files"""
    base_dir = Path(__file__).parent
    pending_approval_path = base_dir / "Pending_Approval"

    if not pending_approval_path.exists():
        logging.info("Pending_Approval folder does not exist")
        pending_approval_path.mkdir(exist_ok=True)  # Create if it doesn't exist
        return False

    # Check if folder contains any files
    files = list(pending_approval_path.iterdir())
    return len(files) > 0


def run_claude_command(command_type="process_needs_action"):
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
            cwd=str(Path(__file__).parent)  # Run in the current directory
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
        logging.error("Claude CLI not found. Please ensure it's installed and in PATH")
        return False
    except Exception as e:
        logging.error(f"Unexpected error running Claude command: {str(e)}")
        return False


def process_approved_files():
    """Process files that have been moved to the /Approved folder"""
    base_dir = Path(__file__).parent
    approved_path = base_dir / "Approved"
    done_path = base_dir / "Done"

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

            # Here you would implement the actual action based on file content
            # For now, we'll just move it to Done after processing
            try:
                # Move to Done folder
                done_file_path = done_path / file_path.name
                file_path.rename(done_file_path)
                logging.info(f"Moved approved file to Done: {file_path.name}")
            except Exception as e:
                logging.error(f"Error moving approved file: {e}")

    return True


def run_business_audit():
    """Run the weekly business audit and generate CEO briefing"""
    base_dir = Path(__file__).parent
    business_goals_path = base_dir / "Business_Goals.md"

    # Check if it's time to run the weekly audit (simplified - run daily for testing)
    current_time = datetime.now()
    if current_time.hour == 7 and current_time.minute < 5:  # Around 7:00 AM
        if business_goals_path.exists():
            logging.info("Running weekly business audit...")
            try:
                # Execute Claude to perform the audit
                cmd = ["claude", "Run business_audit skill"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(base_dir)
                )

                if result.returncode == 0:
                    logging.info("Business audit completed successfully")
                else:
                    logging.error(f"Business audit failed: {result.stderr}")
            except Exception as e:
                logging.error(f"Error running business audit: {e}")


def main():
    logging.info("Starting improved orchestrator...")

    while True:
        try:
            # Check for needs action files
            if check_needs_action_folder():
                logging.info("Found files in Needs_Action folder, triggering Claude command")
                run_claude_command("process_needs_action")

            # Check for pending approval files
            if check_pending_approval_folder():
                logging.info("Found files in Pending_Approval folder, triggering Claude approval processing")
                run_claude_command("process_approval")

            # Process any approved files
            process_approved_files()

            # Run business audit if needed
            run_business_audit()

            # Wait for 60 seconds before next check
            time.sleep(60)

        except KeyboardInterrupt:
            logging.info("Orchestrator stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in orchestrator loop: {str(e)}")
            # Continue the loop even if there's an error
            time.sleep(60)


# Create the skills documentation files for the new functionality
def create_skill_files():
    """Create documentation files for the new skills"""
    base_dir = Path(__file__).parent

    # Create process_approval_skill.md
    approval_skill_content = """# Agent Skill: process_approval

## Purpose
Automated processing of files in the /Pending_Approval folder to handle human-in-the-loop approval workflows.

## Behavior
1. Scan /Pending_Approval folder for new approval request files
2. For each file:
   - Read approval request metadata (action type, parameters, reason)
   - Validate the request against company policies
3. If approved (file moved to /Approved folder):
   - Execute the requested action using appropriate MCP
   - Log the action in /Logs
   - Move the file to /Done folder
4. If rejected (file moved to /Rejected folder):
   - Log the rejection
   - Move the file to /Done folder
5. Update Dashboard.md with action status

## Constraints
- Only execute actions that have been explicitly approved
- Maintain security protocols for sensitive operations
- Log all actions for audit purposes
- Do not execute any unapproved actions
"""

    with open(base_dir / "process_approval_skill.md", "w") as f:
        f.write(approval_skill_content)

    # Create business_audit_skill.md
    audit_skill_content = """# Agent Skill: business_audit

## Purpose
Perform weekly business audit and generate CEO briefing based on company metrics and goals.

## Behavior
1. Read Business_Goals.md to understand current objectives
2. Scan /Done folder from the past week to identify completed tasks
3. Check accounting files for revenue and expenses
4. Generate a CEO briefing with:
   - Executive summary
   - Revenue analysis
   - Completed tasks
   - Bottleneck identification
   - Proactive suggestions
5. Save briefing to /Briefings folder with date stamp
6. Update Dashboard.md with key metrics

## Constraints
- Operate only within the vault directory
- Use only available data files for analysis
- Format briefing in standard CEO briefing template
- Include relevant metrics based on Business_Goals.md
"""

    with open(base_dir / "business_audit_skill.md", "w") as f:
        f.write(audit_skill_content)


if __name__ == "__main__":
    # Create skill documentation files at startup
    create_skill_files()
    main()
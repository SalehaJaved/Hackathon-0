"""
Scheduler for the Personal AI Employee Hackathon (Silver Tier)

This script handles scheduling of various tasks including:
- Daily briefings
- Social media posts
- Weekly audits
- Regular monitoring tasks
"""

import time
import schedule
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import json
import threading


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)


def run_business_audit():
    """Run the weekly business audit and generate CEO briefing"""
    try:
        logging.info("Running weekly business audit...")
        result = subprocess.run(
            ["python", "business_briefing_generator.py"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent)
        )

        if result.returncode == 0:
            logging.info("Business audit completed successfully")
        else:
            logging.error(f"Business audit failed: {result.stderr}")
    except Exception as e:
        logging.error(f"Error running business audit: {e}")


def run_daily_check():
    """Run daily checks and updates"""
    try:
        logging.info("Running daily checks...")

        # Update dashboard with daily metrics
        update_dashboard_daily()

        # Check for scheduled posts that need publishing today
        check_scheduled_posts()

        logging.info("Daily checks completed")
    except Exception as e:
        logging.error(f"Error in daily checks: {e}")


def update_dashboard_daily():
    """Update dashboard with daily metrics"""
    base_dir = Path(__file__).parent
    dashboard_path = base_dir / "Dashboard.md"

    current_time = datetime.now()

    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
    else:
        dashboard_content = "# Dashboard\n\n## Recent Activity\n"

    # Add today's activity marker
    new_activity = f"- [{current_time.strftime('%Y-%m-%d %H:%M')}] Daily check completed\n"

    # Find the recent activity section or add it
    if "## Recent Activity" in dashboard_content:
        dashboard_content = dashboard_content.replace(
            "## Recent Activity",
            f"## Recent Activity\n{new_activity}"
        )
    else:
        dashboard_content += f"\n## Recent Activity\n{new_activity}"

    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_content)


def check_scheduled_posts():
    """Check for and publish any scheduled social media posts"""
    base_dir = Path(__file__).parent
    pending_approval_dir = base_dir / "Pending_Approval"

    if not pending_approval_dir.exists():
        return

    current_time = datetime.now()

    for file_path in pending_approval_dir.iterdir():
        if file_path.suffix.lower() == '.md':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for schedule_time in the frontmatter
                if 'schedule_time:' in content:
                    lines = content.split('\n')
                    for line in lines:
                        if 'schedule_time:' in line:
                            try:
                                scheduled_time_str = line.split(':', 1)[1].strip()
                                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))

                                # If the scheduled time has passed, move to approved
                                if current_time >= scheduled_time:
                                    approved_dir = base_dir / "Approved"
                                    approved_dir.mkdir(exist_ok=True)

                                    approved_path = approved_dir / file_path.name
                                    file_path.rename(approved_path)

                                    logging.info(f"Moved scheduled post to approval: {file_path.name}")

                                break
                            except ValueError:
                                continue  # Skip invalid date formats
            except Exception as e:
                logging.error(f"Error processing scheduled post {file_path.name}: {e}")


def run_linkedin_campaign_monitor():
    """Monitor LinkedIn campaigns"""
    logging.info("Monitoring LinkedIn campaigns...")

    # In a real implementation, you would check campaign status
    # For now, just log the activity
    logging.info("LinkedIn campaign monitoring completed")


def setup_schedules():
    """Set up all scheduled tasks"""
    logging.info("Setting up schedules...")

    # Daily tasks
    schedule.every().day.at("08:00").do(run_daily_check)  # Daily check at 8 AM
    schedule.every().day.at("07:00").do(run_business_audit)  # Business audit at 7 AM (for weekly only, but we'll check day of week inside)

    # Weekly tasks - only run on Sunday
    schedule.every().sunday.at("19:00").do(run_business_audit)  # Weekly CEO briefing on Sunday at 7 PM

    # LinkedIn campaign monitoring (daily)
    schedule.every().day.at("10:00").do(run_linkedin_campaign_monitor)
    schedule.every().day.at("15:00").do(run_linkedin_campaign_monitor)

    logging.info("All schedules set up")


def run_scheduler():
    """Main scheduler loop"""
    logging.info("Starting AI Employee Scheduler...")
    setup_schedules()

    # Run pending jobs once at startup
    schedule.run_pending()

    while True:
        try:
            # Check for scheduled jobs
            schedule.run_pending()

            # Check for scheduled social media posts
            check_scheduled_posts()

            # Wait a bit before checking again
            time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")
            break
        except Exception as e:
            logging.error(f"Error in scheduler: {e}")
            time.sleep(60)  # Wait before continuing


if __name__ == "__main__":
    run_scheduler()
"""
Monday Morning CEO Briefing Generator for the Personal AI Employee Hackathon

This script generates weekly business briefings based on completed tasks,
financial transactions, and business goals.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path


def generate_business_briefing():
    """Generate the weekly business briefing"""
    base_dir = Path(__file__).parent

    # Create necessary directories
    briefings_dir = base_dir / "Briefings"
    briefings_dir.mkdir(exist_ok=True)

    done_dir = base_dir / "Done"
    done_dir.mkdir(exist_ok=True)

    logs_dir = base_dir / "Logs"
    logs_dir.mkdir(exist_ok=True)

    # Get current date and calculate the week period
    current_date = datetime.now()
    start_of_week = current_date - timedelta(days=current_date.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Format dates for use in the briefing
    week_start_str = start_of_week.strftime("%Y-%m-%d")
    week_end_str = end_of_week.strftime("%Y-%m-%d")
    briefing_date_str = current_date.strftime("%Y-%m-%d_%A")

    # Read business goals if available
    business_goals_path = base_dir / "Business_Goals.md"
    business_goals = "No specific goals defined"
    if business_goals_path.exists():
        with open(business_goals_path, 'r', encoding='utf-8') as f:
            business_goals = f.read()

    # Count completed tasks from the week
    completed_tasks = []
    revenue_amount = 0
    expenses_amount = 0

    if done_dir.exists():
        for file_path in done_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.md', '.txt']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    completed_tasks.append({
                        'file': file_path.name,
                        'content': content[:200]  # First 200 chars as preview
                    })

    # Read recent logs to extract financial information
    recent_logs = []
    if logs_dir.exists():
        for log_file in logs_dir.iterdir():
            if log_file.is_file() and log_file.suffix == '.json':
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                        if isinstance(log_data, list):
                            recent_logs.extend(log_data)
                        else:
                            recent_logs.append(log_data)
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON files

    # Analyze logs for financial transactions
    for log_entry in recent_logs:
        if isinstance(log_entry, dict):
            # Look for financial actions in logs
            action_type = log_entry.get('action_type', '')
            if 'payment' in action_type.lower() or 'invoice' in action_type.lower():
                amount = log_entry.get('amount', 0)
                if amount > 0:
                    revenue_amount += amount
                else:
                    expenses_amount += abs(amount)

    # Identify potential bottlenecks (long-running tasks)
    bottlenecks = []
    # This would be more sophisticated in a real implementation
    if len(completed_tasks) > 0:
        bottlenecks.append({
            'task': 'Initial assessment',
            'expected': 'Varies',
            'actual': 'Varies',
            'delay': 'To be determined'
        })

    # Generate proactive suggestions
    suggestions = []
    if revenue_amount < 1000:  # Example threshold
        suggestions.append({
            'type': 'Revenue',
            'suggestion': 'Revenue is below expected thresholds. Consider focusing on sales activities.',
            'action': 'Move to /Pending_Approval'
        })

    if expenses_amount > revenue_amount:
        suggestions.append({
            'type': 'Cost Optimization',
            'suggestion': f'Expenses (${expenses_amount}) exceed revenue (${revenue_amount}). Review expenses.',
            'action': 'Move to /Pending_Approval'
        })

    # Create briefing content
    briefing_content = f"""---
generated: {current_date.isoformat()}
period: {week_start_str} to {week_end_str}
---

# Monday Morning CEO Briefing - Week of {week_start_str}

## Executive Summary
This week's business review shows performance based on completed tasks and financial metrics. There {'are' if revenue_amount > 0 else 'are no'} revenue transactions recorded.

## Business Goals Overview
{business_goals[:500]}  # First 500 chars of business goals

## Revenue Analysis
- **This Week**: ${revenue_amount:.2f}
- **MTD**: ${revenue_amount:.2f} (Estimated based on current week)
- **Trend**: {'Positive' if revenue_amount > 0 else 'Needs attention'}

## Completed Tasks ({len(completed_tasks)} items)
"""

    for i, task in enumerate(completed_tasks[:10]):  # Limit to 10 tasks for brevity
        briefing_content += f"- [{task['file']}]({task['file']})\n"

    if len(completed_tasks) > 10:
        briefing_content += f"- ... and {len(completed_tasks) - 10} more\n"

    briefing_content += f"""

## Bottlenecks ({{len(bottlenecks)}} identified)
"""

    for bottleneck in bottlenecks:
        briefing_content += f"""
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| {bottleneck['task']} | {bottleneck['expected']} | {bottleneck['actual']} | {bottleneck['delay']} |
"""

    briefing_content += f"""

## Proactive Suggestions

### Cost Optimization
"""

    for suggestion in suggestions:
        if suggestion['type'] == 'Cost Optimization':
            briefing_content += f"- **{suggestion['type']}**: {suggestion['suggestion']}\n"
            briefing_content += f"  - [ACTION] {suggestion['action']}\n\n"

    briefing_content += f"""
### Revenue Enhancement
"""

    for suggestion in suggestions:
        if suggestion['type'] == 'Revenue':
            briefing_content += f"- **{suggestion['type']}**: {suggestion['suggestion']}\n"
            briefing_content += f"  - [ACTION] {suggestion['action']}\n\n"

    briefing_content += f"""
## Upcoming Deadlines
- This week: Continue current projects
- Next week: Plan for following week's objectives

---
*Generated by AI Employee v0.1*
"""

    # Save the briefing to a file
    briefing_filename = f"{briefing_date_str}_CEO_Briefing.md"
    briefing_path = briefings_dir / briefing_filename

    with open(briefing_path, 'w', encoding='utf-8') as f:
        f.write(briefing_content)

    # Update Dashboard.md with latest briefing info
    dashboard_path = base_dir / "Dashboard.md"
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
    else:
        dashboard_content = "# Dashboard\n\n## Recent Briefings\n"

    # Add briefing info to dashboard
    briefing_info = f"- [{briefing_filename}]({briefing_filename}) - Generated {current_date.strftime('%Y-%m-%d %H:%M')}\n"

    # Find the recent briefings section or add it
    if "## Recent Briefings" in dashboard_content:
        dashboard_content = dashboard_content.replace(
            "## Recent Briefings",
            f"## Recent Briefings\n{briefing_info}"
        )
    else:
        dashboard_content += f"\n## Recent Briefings\n{briefing_info}"

    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_content)

    print(f"Business briefing generated: {briefing_filename}")
    return briefing_path


def main():
    """Main function to run the briefing generator"""
    try:
        briefing_path = generate_business_briefing()
        print(f"Successfully generated CEO briefing at: {briefing_path}")
    except Exception as e:
        print(f"Error generating business briefing: {e}")


if __name__ == "__main__":
    main()
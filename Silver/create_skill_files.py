"""
Script to create the missing skill files for the AI Employee
"""

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

with open("process_approval_skill.md", "w") as f:
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

with open("business_audit_skill.md", "w") as f:
    f.write(audit_skill_content)

print("Created process_approval_skill.md and business_audit_skill.md")
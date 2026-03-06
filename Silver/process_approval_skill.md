# Agent Skill: process_approval

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

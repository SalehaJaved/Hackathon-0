# Agent Skill: process_needs_action

## Purpose
Automated processing of files in the /Needs_Action folder to streamline workflow and maintain organized records.

## Behavior
1. Scan /Needs_Action folder for new files
2. For each file:
   - Read metadata (created date, author, tags, priority)
   - Summarize content (key points, requirements, deadlines)
   - Suggest next action (approve, delegate, schedule, escalate)
3. Create a Plan file in /Plans with:
   - Action items derived from the file
   - Assigned resources (if applicable)
   - Timeline for completion
4. Move completed files to /Done folder
5. Log action in /Logs/YYYY-MM-DD.json with:
   - Timestamp
   - File processed
   - Action taken
   - Next steps

## Constraints
- Operate only within the vault directory
- Do not take external actions
- Do not use MCP (Managed Control Plane)
- Maintain file integrity during movement
- Follow structured thinking methodology
# Agent Skill: business_audit

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

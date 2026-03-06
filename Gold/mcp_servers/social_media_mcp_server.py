"""
Social Media MCP Server for the Personal AI Employee Hackathon

This server provides social media posting capabilities through the Model Context Protocol (MCP).
It allows Claude Code to post on LinkedIn, Twitter, and other platforms.
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp.server import Server
from mcp.types import CallToolResult, Tool, TextContent, Prompt
from pathlib import Path
import os
from datetime import datetime
import time


# Create the MCP servers directory if it doesn't exist
mcp_dir = Path(__file__).parent
mcp_dir.mkdir(exist_ok=True)

# Initialize the MCP server
server = Server("social-media-mcp-server")


@server.list_prompts()
async def handle_list_prompts() -> List[Prompt]:
    """List available social media prompts"""
    return [
        Prompt(
            name="post_linkedin",
            description="Create a LinkedIn post",
        ),
        Prompt(
            name="post_twitter",
            description="Create a Twitter/X post",
        ),
        Prompt(
            name="post_facebook",
            description="Create a Facebook post",
        ),
        Prompt(
            name="schedule_post",
            description="Schedule a social media post",
        )
    ]


@server.get_prompt()
async def handle_get_prompt(name: str) -> Prompt:
    """Get a specific social media prompt"""
    if name == "post_linkedin":
        return Prompt(
            name="post_linkedin",
            description="Create a LinkedIn post",
            messages=[
                {
                    "role": "user",
                    "content": "Create a LinkedIn post with the following content and optional image."
                }
            ]
        )
    elif name == "post_twitter":
        return Prompt(
            name="post_twitter",
            description="Create a Twitter/X post",
            messages=[
                {
                    "role": "user",
                    "content": "Create a Twitter/X post with the following content."
                }
            ]
        )
    elif name == "post_facebook":
        return Prompt(
            name="post_facebook",
            description="Create a Facebook post",
            messages=[
                {
                    "role": "user",
                    "content": "Create a Facebook post with the following content and optional image."
                }
            ]
        )
    elif name == "schedule_post":
        return Prompt(
            name="schedule_post",
            description="Schedule a social media post",
            messages=[
                {
                    "role": "user",
                    "content": "Schedule a social media post for a future date/time."
                }
            ]
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available social media tools"""
    return [
        Tool(
            name="post_linkedin",
            description="Post content to LinkedIn",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Post content"},
                    "headline": {"type": "string", "description": "Post headline"},
                    "hashtags": {"type": "array", "items": {"type": "string"}, "description": "Hashtags to include"},
                    "image_path": {"type": "string", "description": "Path to image file to attach"}
                },
                "required": ["content", "headline"]
            }
        ),
        Tool(
            name="post_twitter",
            description="Post content to Twitter/X",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Tweet content (max 280 characters)"},
                    "hashtags": {"type": "array", "items": {"type": "string"}, "description": "Hashtags to include"}
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="post_facebook",
            description="Post content to Facebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Post content"},
                    "headline": {"type": "string", "description": "Post headline"},
                    "hashtags": {"type": "array", "items": {"type": "string"}, "description": "Hashtags to include"},
                    "image_path": {"type": "string", "description": "Path to image file to attach"}
                },
                "required": ["content", "headline"]
            }
        ),
        Tool(
            name="schedule_post",
            description="Schedule a social media post for future publication",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "description": "Social media platform (linkedin, twitter, facebook)"},
                    "content": {"type": "string", "description": "Post content"},
                    "schedule_time": {"type": "string", "description": "ISO format datetime for scheduling"},
                    "headline": {"type": "string", "description": "Post headline"}
                },
                "required": ["platform", "content", "schedule_time"]
            }
        ),
        Tool(
            name="create_linkedin_campaign",
            description="Create a LinkedIn campaign to generate sales",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Name of the campaign"},
                    "target_audience": {"type": "string", "description": "Description of target audience"},
                    "content": {"type": "string", "description": "Campaign content"},
                    "duration_days": {"type": "number", "description": "Duration of the campaign in days"}
                },
                "required": ["campaign_name", "target_audience", "content"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for social media operations"""
    try:
        if name == "post_linkedin":
            result = await post_linkedin_tool(arguments)
        elif name == "post_twitter":
            result = await post_twitter_tool(arguments)
        elif name == "post_facebook":
            result = await post_facebook_tool(arguments)
        elif name == "schedule_post":
            result = await schedule_post_tool(arguments)
        elif name == "create_linkedin_campaign":
            result = await create_linkedin_campaign_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return CallToolResult(content=[TextContent(type="text", text=result)])
    except Exception as e:
        error_msg = f"Error executing {name} tool: {str(e)}"
        return CallToolResult(content=[TextContent(type="text", text=error_msg)])


async def post_linkedin_tool(args: Dict[str, Any]) -> str:
    """Create a LinkedIn post draft"""
    return await create_social_post_draft("linkedin", args)


async def post_twitter_tool(args: Dict[str, Any]) -> str:
    """Create a Twitter/X post draft"""
    return await create_social_post_draft("twitter", args)


async def post_facebook_tool(args: Dict[str, Any]) -> str:
    """Create a Facebook post draft"""
    return await create_social_post_draft("facebook", args)


async def schedule_post_tool(args: Dict[str, Any]) -> str:
    """Schedule a social media post for future publication"""
    base_dir = Path(__file__).parent.parent
    pending_approval_dir = base_dir / "Pending_Approval"
    pending_approval_dir.mkdir(exist_ok=True)

    # Verify the schedule_time is in the future
    try:
        schedule_time = datetime.fromisoformat(args.get('schedule_time', '').replace('Z', '+00:00'))
        if schedule_time < datetime.now():
            return "ERROR: Schedule time must be in the future"
    except ValueError:
        return "ERROR: Invalid schedule time format. Use ISO format (e.g., 2026-03-15T10:30:00)"

    # Create scheduled post file
    platform = args.get('platform', 'unknown')
    safe_headline = "".join(c for c in args.get('headline', 'scheduled_post') if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_headline = safe_headline[:50]
    filename = f"SCHEDULED_{platform.upper()}_{safe_headline}_{schedule_time.strftime('%Y%m%d_%H%M%S')}.md"
    filepath = pending_approval_dir / filename

    content = f"""---
type: scheduled_social_post
platform: {platform}
schedule_time: {args.get('schedule_time', '')}
status: pending_approval
---

# Scheduled Social Media Post

**Platform:** {platform}
**Schedule Time:** {args.get('schedule_time', '')}

## Content
{args.get('content', '')}

## Approval Required
Move this file to /Approved to schedule this post.
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return f"Scheduled post saved to {filepath} for approval"


async def create_linkedin_campaign_tool(args: Dict[str, Any]) -> str:
    """Create a LinkedIn campaign to generate sales"""
    base_dir = Path(__file__).parent.parent
    pending_approval_dir = base_dir / "Pending_Approval"
    pending_approval_dir.mkdir(exist_ok=True)

    # Create campaign plan file
    campaign_name = args.get('campaign_name', 'linkedin_campaign')
    safe_campaign_name = "".join(c for c in campaign_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_campaign_name = safe_campaign_name[:50]
    filename = f"LINKEDIN_CAMPAIGN_{safe_campaign_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = pending_approval_dir / filename

    duration = args.get('duration_days', 30)
    content = f"""---
type: linkedin_campaign
campaign_name: {campaign_name}
target_audience: {args.get('target_audience', 'N/A')}
duration_days: {duration}
status: pending_approval
---

# LinkedIn Campaign Plan: {campaign_name}

## Target Audience
{args.get('target_audience', 'N/A')}

## Campaign Content
{args.get('content', '')}

## Duration
{duration} days

## Expected Outcomes
- Generate leads
- Increase brand awareness
- Drive sales conversions

## Approval Required
Move this file to /Approved to start this campaign.
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return f"LinkedIn campaign plan saved to {filepath} for approval"


async def create_social_post_draft(platform: str, args: Dict[str, Any]) -> str:
    """Create a social media post draft in the Pending Approval folder"""
    base_dir = Path(__file__).parent.parent
    pending_approval_dir = base_dir / "Pending_Approval"
    pending_approval_dir.mkdir(exist_ok=True)

    # Check if running in dry-run mode
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

    if dry_run:
        return f"[DRY RUN] Would create {platform} post with content: {args.get('content', '')[:100]}..."

    # Create draft filename
    safe_headline = "".join(c for c in args.get('headline', f'{platform}_post') if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_headline = safe_headline[:50]
    filename = f"{platform.upper()}_POST_{safe_headline}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    draft_path = pending_approval_dir / filename

    # Create draft content
    hashtags = ' '.join([f"#{tag}" for tag in args.get('hashtags', [])])
    content = f"""---
type: social_post_draft
platform: {platform}
status: pending_approval
created: {datetime.now().isoformat()}
---

# Social Media Post Draft

**Platform:** {platform}
**Headline:** {args.get('headline', '')}

## Content
{args.get('content', '')}

## Hashtags
{hashtags}

## Additional Notes
"""

    if args.get('image_path'):
        content += f"\n**Image:** {args.get('image_path')}\n"

    content += f"""
## Approval Required
Move this file to /Approved to publish this {platform} post.
"""

    with open(draft_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Log the action
    log_social_action("create_draft", platform, args.get('headline', ''))

    return f"Social media draft saved to {draft_path} for approval"


def log_social_action(action_type: str, platform: str, content: str):
    """Log social media action to the vault"""
    base_dir = Path(__file__).parent.parent
    logs_dir = base_dir / "Logs"
    logs_dir.mkdir(exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "actor": "social_media_mcp_server",
        "target": platform,
        "parameters": {"content": content[:100]},  # First 100 chars
        "result": "success"
    }

    log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    logs = []

    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(log_entry)

    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)


if __name__ == "__main__":
    print("Social Media MCP Server ready")
    print("Configure in Claude Code with:")
    print({
        "name": "social-media-mcp",
        "command": "python",
        "args": [str(Path(__file__).absolute())],
    })
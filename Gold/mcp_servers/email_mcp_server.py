"""
Email MCP Server for the Personal AI Employee Hackathon

This server provides email capabilities through the Model Context Protocol (MCP).
It allows Claude Code to send emails, drafts, and manage email interactions.
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp.server import Server
from mcp.types import CallToolResult, Tool, TextContent, Prompt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os
from datetime import datetime


# Create the MCP servers directory if it doesn't exist
mcp_dir = Path(__file__).parent
mcp_dir.mkdir(exist_ok=True)

# Initialize the MCP server
server = Server("email-mcp-server")


@server.list_prompts()
async def handle_list_prompts() -> List[Prompt]:
    """List available email-related prompts"""
    return [
        Prompt(
            name="send_email",
            description="Send an email to a recipient",
        ),
        Prompt(
            name="draft_email",
            description="Draft an email",
        ),
        Prompt(
            name="email_templates",
            description="Get available email templates",
        )
    ]


@server.get_prompt()
async def handle_get_prompt(name: str) -> Prompt:
    """Get a specific email prompt"""
    if name == "send_email":
        return Prompt(
            name="send_email",
            description="Send an email to a recipient",
            messages=[
                {
                    "role": "user",
                    "content": "Send an email with the following details: recipient, subject, body, and optional attachments."
                }
            ]
        )
    elif name == "draft_email":
        return Prompt(
            name="draft_email",
            description="Draft an email",
            messages=[
                {
                    "role": "user",
                    "content": "Draft an email with the following details: recipient, subject, and body."
                }
            ]
        )
    elif name == "email_templates":
        return Prompt(
            name="email_templates",
            description="Get available email templates",
            messages=[
                {
                    "role": "user",
                    "content": "Available email templates for different scenarios."
                }
            ]
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available email tools"""
    return [
        Tool(
            name="send_email",
            description="Send an email with subject, body, and optional attachments",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                    "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"},
                    "bcc": {"type": "array", "items": {"type": "string"}, "description": "BCC recipients"},
                    "attachments": {"type": "array", "items": {"type": "string"}, "description": "File paths to attach"}
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="draft_email",
            description="Draft an email without sending",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                    "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"}
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="send_invoice",
            description="Send an invoice email with proper formatting",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "client_name": {"type": "string", "description": "Client name"},
                    "invoice_number": {"type": "string", "description": "Invoice number"},
                    "amount": {"type": "number", "description": "Invoice amount"},
                    "due_date": {"type": "string", "description": "Due date for payment"},
                    "items": {"type": "array", "items": {"type": "string"}, "description": "Invoice line items"}
                },
                "required": ["to", "client_name", "invoice_number", "amount", "due_date", "items"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for email operations"""
    try:
        if name == "send_email":
            result = await send_email_tool(arguments)
        elif name == "draft_email":
            result = await draft_email_tool(arguments)
        elif name == "send_invoice":
            result = await send_invoice_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return CallToolResult(content=[TextContent(type="text", text=result)])
    except Exception as e:
        error_msg = f"Error executing {name} tool: {str(e)}"
        return CallToolResult(content=[TextContent(type="text", text=error_msg)])


async def send_email_tool(args: Dict[str, Any]) -> str:
    """Send an email using SMTP"""
    # Check if running in dry-run mode
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

    if dry_run:
        return f"[DRY RUN] Would send email to: {args.get('to', 'Unknown')}\nSubject: {args.get('subject', 'No Subject')}\nBody: {args.get('body', 'No Body')[:100]}..."

    # Get email configuration from environment
    smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not email_user or not email_password:
        return "ERROR: Email credentials not configured. Please set EMAIL_USER and EMAIL_PASSWORD environment variables."

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = args.get('to', '')
        msg['Subject'] = args.get('subject', '')

        if args.get('cc'):
            msg['Cc'] = ', '.join(args['cc'])

        msg.attach(MIMEText(args.get('body', ''), 'plain'))

        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)

        recipients = [args.get('to', '')]
        if args.get('cc'):
            recipients.extend(args['cc'])
        if args.get('bcc'):
            recipients.extend(args['bcc'])

        text = msg.as_string()
        server.sendmail(email_user, recipients, text)
        server.quit()

        # Log the action
        log_email_action("send_email", args.get('to', ''), args.get('subject', ''))

        return f"Email sent successfully to {args.get('to', '')}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


async def draft_email_tool(args: Dict[str, Any]) -> str:
    """Draft an email and save it to the vault"""
    base_dir = Path(__file__).parent.parent
    drafts_dir = base_dir / "Drafts"
    drafts_dir.mkdir(exist_ok=True)

    # Create draft filename
    safe_subject = "".join(c for c in args.get('subject', 'draft') if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_subject = safe_subject[:50]
    filename = f"draft_{safe_subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    draft_path = drafts_dir / filename

    # Create draft content
    content = f"""---
type: email_draft
status: pending_approval
created: {datetime.now().isoformat()}
to: {args.get('to', '')}
cc: {', '.join(args.get('cc', []))}
---

# Email Draft

**To:** {args.get('to', '')}
**CC:** {', '.join(args.get('cc', []))}
**Subject:** {args.get('subject', '')}

## Body
{args.get('body', '')}

## Approval Required
Move this file to /Approved to send this email.
"""

    with open(draft_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return f"Email draft saved to {draft_path}"


async def send_invoice_tool(args: Dict[str, Any]) -> str:
    """Send an invoice email with proper formatting"""
    # Create invoice body
    items_str = "\n".join([f"- {item}" for item in args.get('items', [])])

    invoice_body = f"""
Dear {args.get('client_name', 'Customer')},

Please find your invoice details below:

**Invoice Number:** {args.get('invoice_number', 'N/A')}
**Amount:** ${args.get('amount', 0):.2f}
**Due Date:** {args.get('due_date', 'N/A')}

**Items:**
{items_str}

Please make payment by the due date. Let me know if you have any questions.

Best regards,
Your AI Employee
"""

    # Use the send_email function with invoice body
    email_args = {
        'to': args.get('to', ''),
        'subject': f"INVOICE {args.get('invoice_number', 'N/A')} - ${args.get('amount', 0):.2f}",
        'body': invoice_body
    }

    return await send_email_tool(email_args)


def log_email_action(action_type: str, recipient: str, subject: str):
    """Log email action to the vault"""
    base_dir = Path(__file__).parent.parent
    logs_dir = base_dir / "Logs"
    logs_dir.mkdir(exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "actor": "email_mcp_server",
        "target": recipient,
        "parameters": {"subject": subject},
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
    import uvicorn

    # To run this MCP server, you would typically use:
    # mcp server run --url http://localhost:3000
    print("Email MCP Server ready")
    print("Configure in Claude Code with:")
    print({
        "name": "email-mcp",
        "command": "python",
        "args": [str(Path(__file__).absolute())],
        "env": {
            "EMAIL_USER": "your_email@example.com",
            "EMAIL_PASSWORD": "your_app_password"
        }
    })
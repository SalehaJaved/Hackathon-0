"""
Email MCP Server for Gold Tier AI Employee
Implements email sending, receiving, and management capabilities
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailMCPServer:
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.audit_log = []

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load email configuration from file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration - in production, this should come from environment
            return {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_tls": True
            }

    async def get_contexts(self) -> List[Dict[str, Any]]:
        """MCP Protocol: Return available contexts"""
        return [
            {
                "type": "context",
                "id": "email_operations",
                "name": "Email Operations",
                "description": "Email sending, receiving, and management operations"
            }
        ]

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """MCP Protocol: Return available prompts"""
        return [
            {
                "type": "prompt",
                "id": "send_email",
                "name": "Send Email",
                "description": "Send an email to specified recipient(s)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"},
                        "cc": {"type": "string", "description": "CC recipients (optional)"},
                        "bcc": {"type": "string", "description": "BCC recipients (optional)"},
                        "attachments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File paths to attach (optional)"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "type": "prompt",
                "id": "draft_email",
                "name": "Draft Email",
                "description": "Create an email draft without sending",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"},
                        "save_to": {"type": "string", "description": "Path to save draft"}
                    },
                    "required": ["to", "subject", "body", "save_to"]
                }
            }
        ]

    async def call_tool(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP Protocol: Execute a tool"""
        try:
            if tool_id == "send_email":
                return await self.send_email(arguments)
            elif tool_id == "draft_email":
                return await self.draft_email(arguments)
            else:
                return {
                    "error": f"Unknown tool: {tool_id}",
                    "success": False
                }
        except Exception as e:
            self.logger.error(f"Error in call_tool: {e}")
            return {
                "error": str(e),
                "success": False
            }

    async def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email using SMTP"""
        try:
            # Get credentials from environment (these should NEVER be hardcoded)
            email_user = self.config.get("email_user") or self.get_env("EMAIL_USER")
            email_password = self.config.get("email_password") or self.get_env("EMAIL_PASSWORD")

            if not email_user or not email_password:
                return {
                    "error": "Email credentials not configured",
                    "success": False
                }

            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = params.get('to', '')
            msg['Subject'] = params.get('subject', '')

            # Add body
            body = params.get('body', '')
            msg.attach(MIMEText(body, 'plain'))

            # Add attachments if provided
            attachments = params.get('attachments', [])
            for file_path in attachments:
                try:
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {Path(file_path).name}'
                    )
                    msg.attach(part)
                except Exception as e:
                    self.logger.error(f"Error attaching file {file_path}: {e}")

            # Send email
            server = smtplib.SMTP(self.config.get('smtp_server', 'smtp.gmail.com'),
                                self.config.get('smtp_port', 587))
            server.starttls() if self.config.get('use_tls', True) else None
            server.login(email_user, email_password)

            text = msg.as_string()
            server.sendmail(email_user, params['to'], text)
            server.quit()

            # Log the action
            self.log_action({
                "type": "email_sent",
                "timestamp": datetime.now().isoformat(),
                "to": params['to'],
                "subject": params['subject'],
                "status": "success"
            })

            return {
                "success": True,
                "result": f"Email sent successfully to {params['to']}",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            self.log_action({
                "type": "email_send_failed",
                "timestamp": datetime.now().isoformat(),
                "to": params.get('to', ''),
                "subject": params.get('subject', ''),
                "error": str(e),
                "status": "failed"
            })
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }

    async def draft_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an email draft without sending"""
        try:
            draft_content = f"""---
draft_date: {datetime.now().isoformat()}
status: pending_approval
---

# Email Draft

**To:** {params.get('to', '')}
**Subject:** {params.get('subject', '')}

## Body
{params.get('body', '')}

## Instructions
Review this email draft and move to /Approved folder to send, or /Rejected folder to discard.
"""

            # Save draft to specified location
            save_path = Path(params.get('save_to', 'email_draft.md'))

            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Write draft
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)

            # Log the action
            self.log_action({
                "type": "email_draft_created",
                "timestamp": datetime.now().isoformat(),
                "file_path": str(save_path),
                "to": params.get('to', ''),
                "subject": params.get('subject', ''),
                "status": "success"
            })

            return {
                "success": True,
                "result": f"Email draft saved to {save_path}",
                "file_path": str(save_path)
            }

        except Exception as e:
            self.logger.error(f"Failed to create email draft: {e}")
            return {
                "success": False,
                "error": f"Failed to create email draft: {str(e)}"
            }

    def get_env(self, key: str) -> str:
        """Get environment variable"""
        import os
        return os.getenv(key)

    def log_action(self, action: Dict[str, Any]):
        """Log an action to the audit trail"""
        self.audit_log.append(action)

        # Also write to a log file
        log_file = Path("Logs") / f"email_mcp_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(action) + "\n")

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the email MCP server"""
        try:
            # Check if required configuration is available
            email_user = self.config.get("email_user") or self.get_env("EMAIL_USER")
            email_password = self.config.get("email_password") or self.get_env("EMAIL_PASSWORD")

            status = "healthy" if email_user and email_password else "degraded"

            return {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "smtp_configured": bool(self.config.get("smtp_server")),
                    "credentials_available": bool(email_user and email_password),
                    "last_action": self.audit_log[-1] if self.audit_log else None
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Example usage
if __name__ == "__main__":
    import os
    os.makedirs("Logs", exist_ok=True)

    server = EmailMCPServer()

    # Example of how to use
    async def example():
        # This is just a demonstration - would need proper credentials to actually work
        result = await server.health_check()
        print(json.dumps(result, indent=2))

        prompts = await server.list_prompts()
        print(f"Available prompts: {len(prompts)}")

    # In a real implementation, this would be run as part of the MCP server ecosystem
    print("Email MCP Server initialized")
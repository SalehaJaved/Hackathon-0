"""
Comprehensive Audit Logger for Gold Tier AI Employee
Implements required audit logging for all actions taken by the AI system
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class AuditLogger:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger('AuditLogger')
        self.logger.setLevel(logging.INFO)

        # Create file handler that rotates daily
        handler = logging.FileHandler(self.logs_dir / 'audit.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_action(self,
                   action_type: str,
                   actor: str,
                   target: str,
                   parameters: Dict[str, Any],
                   approval_status: str = "approved",
                   approved_by: str = "system",
                   result: str = "success",
                   additional_info: Optional[Dict[str, Any]] = None):
        """Log an action taken by the system"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "result": result,
            "additional_info": additional_info or {}
        }

        # Write to daily log file
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f"{date_str}_audit.json"

        # Read existing log entries or create new list
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        logs.append(log_entry)

        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)

        # Also log to the main audit log
        self.logger.info(f"Action: {action_type}, Target: {target}, Result: {result}")

        return log_entry

    def log_error(self,
                  error_type: str,
                  error_message: str,
                  context: Dict[str, Any],
                  severity: str = "medium"):
        """Log an error or failure"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "severity": severity
        }

        # Write to daily log file
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f"{date_str}_audit.json"

        # Read existing log entries or create new list
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        logs.append(log_entry)

        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)

        # Also log to the main audit log with appropriate level
        if severity.lower() == "high":
            self.logger.error(f"ERROR: {error_type} - {error_message}")
        else:
            self.logger.warning(f"ERROR: {error_type} - {error_message}")

        return log_entry


# Example usage function
def create_audit_logger(vault_path: str = None):
    """Create and return an audit logger instance"""
    if vault_path is None:
        vault_path = str(Path(__file__).parent)
    return AuditLogger(vault_path)


if __name__ == "__main__":
    # Example usage
    audit_logger = create_audit_logger()

    # Log a sample action
    audit_logger.log_action(
        action_type="email_send",
        actor="claude_code",
        target="client@example.com",
        parameters={"subject": "Invoice #123", "body_length": 250},
        approval_status="approved",
        approved_by="human",
        result="success"
    )

    print("Audit log entry created successfully")
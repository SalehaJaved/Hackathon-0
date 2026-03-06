"""
Expense Policy Enforcer for the Personal AI Employee Hackathon

This module enforces expense policies by monitoring transactions and flagging violations.
It checks for violations like expenses above thresholds, duplicate expenses, etc.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class ExpensePolicyEnforcer:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Logs"
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"

        # Create directories if they don't exist
        self.logs_dir.mkdir(exist_ok=True)
        self.needs_action_dir.mkdir(exist_ok=True)
        self.pending_approval_dir.mkdir(exist_ok=True)

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'expense_policy.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_expense_policy(self, transaction: Dict[str, Any]) -> List[str]:
        """Check a single transaction against expense policies"""
        violations = []

        # Check if amount exceeds approval threshold
        amount = transaction.get('amount', 0)
        if amount > 100:  # Policy: amounts > $100 need approval
            violations.append(f"Amount ${amount} exceeds $100 approval threshold")

        if amount > 500:  # Policy: amounts > $500 need special approval
            violations.append(f"Amount ${amount} exceeds $500 special approval threshold")

        # Check for suspicious patterns
        description = transaction.get('description', '').lower()
        if any(suspicious in description for suspicious in ['cash', 'gift', 'personal']):
            violations.append(f"Transaction description contains suspicious terms: {description}")

        # Check for duplicate transactions within a short time period
        if self.is_potential_duplicate(transaction):
            violations.append("Potential duplicate transaction detected")

        return violations

    def is_potential_duplicate(self, transaction: Dict[str, Any]) -> bool:
        """Check if this transaction might be a duplicate of recent ones"""
        # Look for transactions with same amount and similar description within the last 24 hours
        recent_transactions = self.get_recent_transactions(hours=24)

        for recent_tx in recent_transactions:
            if (abs(recent_tx.get('amount', 0) - transaction.get('amount', 0)) < 0.01 and
                self.descriptions_are_similar(recent_tx.get('description', ''),
                                            transaction.get('description', ''))):
                return True

        return False

    def descriptions_are_similar(self, desc1: str, desc2: str) -> bool:
        """Check if two transaction descriptions are similar enough to be duplicates"""
        desc1_lower = desc1.lower()
        desc2_lower = desc2.lower()

        # Check if they share significant words
        words1 = set(desc1_lower.split())
        words2 = set(desc2_lower.split())

        # If they share at least 3 common words, consider it potentially duplicate
        common_words = words1.intersection(words2)
        return len(common_words) >= 3

    def get_recent_transactions(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent transactions from log files"""
        recent_transactions = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Look through recent log files
        for log_file in self.logs_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs_data = json.load(f)

                    if isinstance(logs_data, list):
                        for log_entry in logs_data:
                            if log_entry.get('action_type') == 'expense_transaction':
                                timestamp_str = log_entry.get('timestamp')
                                if timestamp_str:
                                    try:
                                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                        if timestamp >= cutoff_time:
                                            recent_transactions.append({
                                                'amount': log_entry.get('parameters', {}).get('amount', 0),
                                                'description': log_entry.get('parameters', {}).get('description', ''),
                                                'timestamp': timestamp_str
                                            })
                                    except ValueError:
                                        continue
            except (json.JSONDecodeError, FileNotFoundError):
                continue

        return recent_transactions

    def process_accounting_file(self, accounting_file: Path):
        """Process an accounting file to check for policy violations"""
        self.logger.info(f"Processing accounting file: {accounting_file.name}")

        try:
            with open(accounting_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # This is a simple implementation - in reality you'd parse the accounting format
            # For now, let's assume it contains JSON transaction data
            try:
                transactions = json.loads(content)
                if not isinstance(transactions, list):
                    transactions = [transactions]  # Handle single transaction
            except json.JSONDecodeError:
                # If not JSON, try to extract simple transaction info
                # This would be implementation-specific based on your accounting format
                self.logger.warning(f"Could not parse {accounting_file.name} as JSON, skipping")
                return

            for i, transaction in enumerate(transactions):
                violations = self.check_expense_policy(transaction)

                if violations:
                    self.create_policy_violation_alert(transaction, violations)

        except Exception as e:
            self.logger.error(f"Error processing accounting file {accounting_file.name}: {e}")

    def create_policy_violation_alert(self, transaction: Dict[str, Any], violations: List[str]):
        """Create an alert for policy violations"""
        # Create a Needs Action file for the violation
        safe_desc = "".join(c for c in transaction.get('description', 'violation') if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_desc = safe_desc[:50]

        filename = f"EXPENSE_VIOLATION_{safe_desc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        alert_path = self.needs_action_dir / filename

        content = f"""---
type: expense_policy_violation
priority: high
status: pending_review
amount: {transaction.get('amount', 0)}
timestamp: {datetime.now().isoformat()}
---

# Expense Policy Violation Alert

## Transaction Details
- **Amount:** ${transaction.get('amount', 0)}
- **Description:** {transaction.get('description', 'N/A')}
- **Date:** {transaction.get('date', 'N/A')}
- **Vendor:** {transaction.get('vendor', 'N/A')}

## Policy Violations Identified
"""

        for violation in violations:
            content += f"- {violation}\n"

        content += f"""
## Required Actions
- [ ] Review transaction for legitimacy
- [ ] Approve if legitimate
- [ ] Reject if policy violation is confirmed
- [ ] Update accounting records if necessary

## Context
This transaction violated one or more expense policies as defined in Company_Handbook.md.
"""

        with open(alert_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.logger.warning(f"Created expense policy violation alert: {filename}")

    def scan_accounting_folder(self):
        """Scan the accounting folder for new files to process"""
        accounting_dir = self.vault_path / "Accounting"

        if not accounting_dir.exists():
            self.logger.info("Accounting directory does not exist, creating it")
            accounting_dir.mkdir(exist_ok=True)
            return

        # Process all .json and .md files in accounting directory
        for file_path in accounting_dir.glob("*.[jJ][sS][oO][nN]"):
            self.process_accounting_file(file_path)

        for file_path in accounting_dir.glob("*.[mM][dD]"):
            self.process_accounting_file(file_path)

    def run_policy_check(self):
        """Run the main policy check cycle"""
        self.logger.info("Starting expense policy check...")

        # Scan accounting folder for new transactions
        self.scan_accounting_folder()

        # Check recent logs for any new expense transactions
        self.check_recent_expenses()

        self.logger.info("Expense policy check completed")


    def check_recent_expenses(self):
        """Check recent expense entries in logs for policy violations"""
        recent_transactions = self.get_recent_transactions(hours=24)

        for transaction in recent_transactions:
            # Only check if it's an expense transaction
            if transaction.get('amount', 0) < 0 or 'expense' in transaction.get('description', '').lower():
                violations = self.check_expense_policy(transaction)

                if violations:
                    self.create_policy_violation_alert(transaction, violations)


def main():
    """Main function to run the expense policy enforcer"""
    vault_path = Path(__file__).parent.parent  # Go up to main vault directory

    enforcer = ExpensePolicyEnforcer(vault_path)
    enforcer.run_policy_check()


if __name__ == "__main__":
    main()
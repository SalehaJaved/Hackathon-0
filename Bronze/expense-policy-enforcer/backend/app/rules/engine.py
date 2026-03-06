"""
Policy Rules Engine - Evaluate expenses against policies
"""
from typing import Dict, List, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PolicyEvaluationResult:
    """Result of policy evaluation"""
    
    def __init__(self):
        self.violations: List[Dict] = []
        self.action: str = "auto_approve"
        self.requires_approval: bool = False
        self.auto_reject: bool = False
    
    def add_violation(self, policy_id: str, policy_name: str, reason: str):
        """Add a policy violation"""
        self.violations.append({
            "policy_id": policy_id,
            "policy_name": policy_name,
            "reason": reason
        })
    
    def set_action(self, action: str):
        """Set the enforcement action"""
        self.action = action
        self.requires_approval = action == "require_approval"
        self.auto_reject = action == "auto_reject"


class RulesEngine:
    """Evaluate expenses against policy rules"""
    
    def __init__(self):
        self.policies: List[Dict] = []
    
    def load_policies(self, policies: List[Dict]):
        """Load policy rules"""
        # Sort by priority (higher priority first)
        self.policies = sorted(
            policies,
            key=lambda p: p.get("priority", 0),
            reverse=True
        )
    
    def evaluate_expense(
        self,
        amount: Decimal,
        category: str,
        vendor: str,
        has_receipt: bool = True
    ) -> PolicyEvaluationResult:
        """
        Evaluate an expense against all active policies
        Returns the most restrictive action required
        """
        result = PolicyEvaluationResult()
        
        for policy in self.policies:
            if not policy.get("active", True):
                continue
            
            violation = self._check_policy(policy, amount, category, vendor, has_receipt)
            
            if violation:
                result.add_violation(
                    policy_id=policy["id"],
                    policy_name=policy["name"],
                    reason=violation
                )
                
                # Update action to most restrictive
                policy_action = policy.get("action", "auto_approve")
                if policy_action == "auto_reject":
                    result.set_action("auto_reject")
                elif policy_action == "require_approval" and result.action != "auto_reject":
                    result.set_action("require_approval")
        
        return result
    
    def _check_policy(
        self,
        policy: Dict,
        amount: Decimal,
        category: str,
        vendor: str,
        has_receipt: bool
    ) -> Optional[str]:
        """
        Check a single policy against expense data
        Returns violation reason if policy is violated, None otherwise
        """
        condition_type = policy.get("condition_type")
        condition = policy.get("condition_json", {})
        
        if condition_type == "amount_threshold":
            return self._check_amount_threshold(condition, amount, policy["name"])
        
        elif condition_type == "category_restriction":
            return self._check_category_restriction(condition, category, policy["name"])
        
        elif condition_type == "vendor_block":
            return self._check_vendor_block(condition, vendor, policy["name"])
        
        elif condition_type == "category_threshold":
            return self._check_category_threshold(condition, amount, category, policy["name"])
        
        elif condition_type == "receipt_required":
            return self._check_receipt_required(condition, amount, has_receipt, policy["name"])
        
        return None
    
    def _check_amount_threshold(
        self,
        condition: Dict,
        amount: Decimal,
        policy_name: str
    ) -> Optional[str]:
        """Check amount threshold policy"""
        threshold = Decimal(str(condition.get("value", 0)))
        operator = condition.get("operator", "greater_than")
        
        if operator == "greater_than" and amount > threshold:
            return f"Amount ${amount} exceeds threshold ${threshold}"
        
        elif operator == "less_than" and amount < threshold:
            return f"Amount ${amount} is below minimum ${threshold}"
        
        return None
    
    def _check_category_restriction(
        self,
        condition: Dict,
        category: str,
        policy_name: str
    ) -> Optional[str]:
        """Check category restriction policy"""
        blocked = condition.get("blocked_categories", [])
        
        if category.lower() in [c.lower() for c in blocked]:
            return f"Category '{category}' is not allowed"
        
        return None
    
    def _check_vendor_block(
        self,
        condition: Dict,
        vendor: str,
        policy_name: str
    ) -> Optional[str]:
        """Check vendor block policy"""
        blocked_vendors = condition.get("blocked_vendors", [])
        
        if vendor.lower() in [v.lower() for v in blocked_vendors]:
            return f"Vendor '{vendor}' is blocked"
        
        return None
    
    def _check_category_threshold(
        self,
        condition: Dict,
        amount: Decimal,
        category: str,
        policy_name: str
    ) -> Optional[str]:
        """Check category-specific threshold policy"""
        target_category = condition.get("category", "")
        threshold = Decimal(str(condition.get("value", 0)))
        
        if category.lower() == target_category.lower() and amount > threshold:
            return f"{category} amount ${amount} exceeds per-diem ${threshold}"
        
        return None
    
    def _check_receipt_required(
        self,
        condition: Dict,
        amount: Decimal,
        has_receipt: bool,
        policy_name: str
    ) -> Optional[str]:
        """Check receipt requirement policy"""
        threshold = Decimal(str(condition.get("threshold", 0)))
        
        if amount > threshold and not has_receipt:
            return f"Receipt required for expenses over ${threshold}"
        
        return None


# Default policies based on Company Handbook
DEFAULT_POLICIES = [
    {
        "id": "policy_001",
        "name": "Manager Approval for Expenses >$100",
        "description": "Any expense above $100 requires prior approval from a manager",
        "condition_type": "amount_threshold",
        "condition_json": {"operator": "greater_than", "value": 100},
        "action": "require_approval",
        "approver_role": "manager",
        "priority": 10,
        "active": True
    },
    {
        "id": "policy_002",
        "name": "Receipt Required for Expenses >$25",
        "description": "Receipts required for reimbursement of expenses over $25",
        "condition_type": "receipt_required",
        "condition_json": {"threshold": 25},
        "action": "flag_for_review",
        "priority": 5,
        "active": True
    }
]


def get_default_policies() -> List[Dict]:
    """Get default policy configuration"""
    return DEFAULT_POLICIES

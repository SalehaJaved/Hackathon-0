"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import enum


class ExpenseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class PolicyAction(str, enum.Enum):
    AUTO_APPROVE = "auto_approve"
    REQUIRE_APPROVAL = "require_approval"
    AUTO_REJECT = "auto_reject"


# Expense Schemas
class ExpenseBase(BaseModel):
    vendor: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, le=100000)
    currency: str = Field(default="USD", max_length=3)
    date: date
    category: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)


class ExpenseCreate(ExpenseBase):
    """Schema for creating an expense"""
    pass


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense"""
    vendor: Optional[str] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    """Schema for expense response"""
    id: str
    user_id: str
    status: ExpenseStatus
    policy_violations: Optional[List[Dict]] = None
    receipt_path: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExpenseSubmitResponse(BaseModel):
    """Schema for expense submission response"""
    id: str
    status: ExpenseStatus
    policy_violations: Optional[List[Dict]] = None
    message: str


# Policy Schemas
class PolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    condition_type: str
    condition_json: Dict[str, Any]
    action: PolicyAction
    approver_role: Optional[str] = None
    priority: int = 0


class PolicyCreate(PolicyBase):
    """Schema for creating a policy"""
    pass


class PolicyUpdate(BaseModel):
    """Schema for updating a policy"""
    name: Optional[str] = None
    description: Optional[str] = None
    condition_json: Optional[Dict[str, Any]] = None
    action: Optional[PolicyAction] = None
    active: Optional[bool] = None


class PolicyResponse(PolicyBase):
    """Schema for policy response"""
    id: str
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Audit Log Schema
class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: str
    expense_id: str
    action: str
    previous_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    reason: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Dashboard Stats
class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    pending_count: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    total_amount: Decimal = Decimal("0.00")
    this_month_amount: Decimal = Decimal("0.00")

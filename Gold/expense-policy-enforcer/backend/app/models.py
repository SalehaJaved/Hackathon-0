"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Integer, Decimal, Date, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class ExpenseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class PolicyAction(str, enum.Enum):
    AUTO_APPROVE = "auto_approve"
    REQUIRE_APPROVAL = "require_approval"
    AUTO_REJECT = "auto_reject"
    FLAG_FOR_REVIEW = "flag_for_review"


class ConditionType(str, enum.Enum):
    AMOUNT_THRESHOLD = "amount_threshold"
    CATEGORY_RESTRICTION = "category_restriction"
    VENDOR_BLOCK = "vendor_block"
    CATEGORY_THRESHOLD = "category_threshold"
    RECEIPT_REQUIRED = "receipt_required"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), default="submitter")  # submitter, manager, admin, finance
    department = Column(String(100))
    manager_id = Column(String(36), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    expenses = relationship("Expense", back_populates="user")


class Expense(Base):
    """Expense model"""
    __tablename__ = "expenses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    vendor = Column(String(255), nullable=False)
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    date = Column(Date, nullable=False)
    category = Column(String(50))
    receipt_path = Column(String(500))
    ocr_data = Column(JSON)
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING, index=True)
    policy_violations = Column(JSON)
    notes = Column(Text)
    approved_by = Column(String(36), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="expenses")


class Policy(Base):
    """Policy rule model"""
    __tablename__ = "policies"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    condition_type = Column(Enum(ConditionType), nullable=False)
    condition_json = Column(JSON, nullable=False)
    action = Column(Enum(PolicyAction), nullable=False)
    approver_role = Column(String(50))
    priority = Column(Integer, default=0)
    active = Column(Boolean, default=True, index=True)
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """Audit log model - immutable"""
    __tablename__ = "audit_log"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    expense_id = Column(String(36), ForeignKey("expenses.id"), index=True)
    policy_id = Column(String(36), ForeignKey("policies.id"))
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    action = Column(String(50), nullable=False, index=True)
    previous_value = Column(JSON)
    new_value = Column(JSON)
    reason = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

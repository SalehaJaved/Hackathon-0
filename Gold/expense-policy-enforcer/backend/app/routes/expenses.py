"""
Expense routes - CRUD operations and workflow
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import os
import shutil
import uuid

from app.database import get_db
from app.models import Expense, ExpenseStatus, User, AuditLog, Policy
from app.schemas import (
    ExpenseCreate, ExpenseResponse, ExpenseSubmitResponse,
    ExpenseUpdate, DashboardStats
)
from app.ocr.processor import process_receipt
from app.rules.engine import RulesEngine

router = APIRouter()

# Configuration
RECEIPT_FOLDER = "backend/receipts"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}


def save_receipt(file: UploadFile, expense_id: str) -> str:
    """Save uploaded receipt file"""
    # Ensure folder exists
    os.makedirs(RECEIPT_FOLDER, exist_ok=True)
    
    # Generate safe filename
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{expense_id}{ext}"
    filepath = os.path.join(RECEIPT_FOLDER, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return filepath


@router.post("/", response_model=ExpenseSubmitResponse)
async def submit_expense(
    vendor: str = Form(...),
    amount: float = Form(...),
    date: str = Form(...),
    category: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    receipt: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new expense with optional receipt upload
    """
    # Generate expense ID
    expense_id = str(uuid.uuid4())
    
    # Process receipt with OCR if uploaded
    ocr_data = None
    receipt_path = None
    
    if receipt and receipt.filename:
        # Validate file type
        ext = os.path.splitext(receipt.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
            )
        
        # Save receipt
        receipt_path = save_receipt(receipt, expense_id)
        
        # Run OCR (skip for PDF in MVP)
        if ext != ".pdf":
            try:
                ocr_data = process_receipt(receipt_path)
                # Use OCR data if form fields are empty
                if ocr_data:
                    vendor = ocr_data.get("vendor", vendor)
                    amount = ocr_data.get("amount", amount)
                    category = ocr_data.get("category", category)
            except Exception as e:
                # OCR failed, continue with manual data
                ocr_data = {"error": str(e), "confidence": 0}
    
    # Get active policies
    result = await db.execute(
        select(Policy).where(Policy.active == True)
    )
    policies = result.scalars().all()
    
    # Evaluate against policies
    engine = RulesEngine()
    engine.load_policies([
        {
            "id": p.id,
            "name": p.name,
            "condition_type": p.condition_type.value,
            "condition_json": p.condition_json,
            "action": p.action.value,
            "priority": p.priority,
            "active": p.active
        }
        for p in policies
    ])
    
    evaluation = engine.evaluate_expense(
        amount=Decimal(str(amount)),
        category=category or "general",
        vendor=vendor,
        has_receipt=receipt_path is not None
    )
    
    # Determine status
    if evaluation.auto_reject:
        status = ExpenseStatus.REJECTED
    elif evaluation.requires_approval:
        status = ExpenseStatus.NEEDS_REVIEW
    else:
        status = ExpenseStatus.APPROVED
    
    # Create expense
    expense = Expense(
        id=expense_id,
        user_id="user_001",  # TODO: Get from auth context
        vendor=vendor,
        amount=Decimal(str(amount)),
        currency="USD",
        date=datetime.strptime(date, "%Y-%m-%d").date() if isinstance(date, str) else date,
        category=category,
        receipt_path=receipt_path,
        ocr_data=ocr_data,
        status=status,
        policy_violations=evaluation.violations if evaluation.violations else None,
        notes=notes
    )
    
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    
    # Log audit
    audit = AuditLog(
        expense_id=expense_id,
        user_id="user_001",
        action="submitted",
        new_value={"vendor": vendor, "amount": str(amount), "status": status.value}
    )
    db.add(audit)
    await db.commit()
    
    # Build response message
    if evaluation.requires_approval:
        message = "Expense submitted. Requires manager approval."
    elif evaluation.auto_reject:
        message = "Expense rejected due to policy violation."
    else:
        message = "Expense auto-approved."
    
    return ExpenseSubmitResponse(
        id=expense_id,
        status=status,
        policy_violations=evaluation.violations if evaluation.violations else None,
        message=message
    )


@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    status: Optional[ExpenseStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List expenses with optional filtering"""
    query = select(Expense).order_by(Expense.created_at.desc())
    
    if status:
        query = query.where(Expense.status == status)
    
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    expenses = result.scalars().all()
    
    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: str, db: AsyncSession = Depends(get_db)):
    """Get expense by ID"""
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id)
    )
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return expense


@router.post("/{expense_id}/approve", response_model=ExpenseResponse)
async def approve_expense(
    expense_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Approve a pending expense"""
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id)
    )
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update status
    expense.status = ExpenseStatus.APPROVED
    expense.approved_by = "user_001"  # TODO: Get from auth
    expense.approved_at = datetime.now()
    
    # Log audit
    audit = AuditLog(
        expense_id=expense_id,
        user_id="user_001",
        action="approved",
        previous_value={"status": expense.status.value},
        new_value={"status": ExpenseStatus.APPROVED.value},
        reason=reason
    )
    db.add(audit)
    await db.commit()
    await db.refresh(expense)
    
    return expense


@router.post("/{expense_id}/reject", response_model=ExpenseResponse)
async def reject_expense(
    expense_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Reject a pending expense"""
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id)
    )
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update status
    expense.status = ExpenseStatus.REJECTED
    
    # Log audit
    audit = AuditLog(
        expense_id=expense_id,
        user_id="user_001",
        action="rejected",
        previous_value={"status": expense.status.value},
        new_value={"status": ExpenseStatus.REJECTED.value},
        reason=reason
    )
    db.add(audit)
    await db.commit()
    await db.refresh(expense)
    
    return expense


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    # Count by status
    pending = await db.execute(
        select(func.count()).where(Expense.status == ExpenseStatus.PENDING)
    )
    pending_count = pending.scalar() or 0
    
    approved = await db.execute(
        select(func.count()).where(Expense.status == ExpenseStatus.APPROVED)
    )
    approved_count = approved.scalar() or 0
    
    rejected = await db.execute(
        select(func.count()).where(Expense.status == ExpenseStatus.REJECTED)
    )
    rejected_count = rejected.scalar() or 0
    
    # Total amount
    total = await db.execute(select(func.sum(Expense.amount)))
    total_amount = total.scalar() or Decimal("0.00")
    
    # This month
    from datetime import date
    first_day = date.today().replace(day=1)
    month_total = await db.execute(
        select(func.sum(Expense.amount)).where(Expense.date >= first_day)
    )
    month_amount = month_total.scalar() or Decimal("0.00")
    
    return DashboardStats(
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        total_amount=total_amount,
        this_month_amount=month_amount
    )

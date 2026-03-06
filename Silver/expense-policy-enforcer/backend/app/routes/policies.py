"""
Policy routes - CRUD operations for policy management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Policy
from app.schemas import PolicyCreate, PolicyResponse, PolicyUpdate

router = APIRouter()


@router.post("/", response_model=PolicyResponse)
async def create_policy(
    policy: PolicyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new policy"""
    db_policy = Policy(
        name=policy.name,
        description=policy.description,
        condition_type=policy.condition_type,
        condition_json=policy.condition_json,
        action=policy.action,
        approver_role=policy.approver_role,
        priority=policy.priority,
        created_by="user_001"  # TODO: Get from auth
    )
    
    db.add(db_policy)
    await db.commit()
    await db.refresh(db_policy)
    
    return db_policy


@router.get("/", response_model=List[PolicyResponse])
async def list_policies(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List all policies"""
    query = select(Policy).order_by(Policy.priority.desc())
    
    if active_only:
        query = query.where(Policy.active == True)
    
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return policies


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    """Get policy by ID"""
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id)
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    policy_update: PolicyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a policy"""
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id)
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Update fields
    if policy_update.name is not None:
        policy.name = policy_update.name
    if policy_update.description is not None:
        policy.description = policy_update.description
    if policy_update.condition_json is not None:
        policy.condition_json = policy_update.condition_json
    if policy_update.action is not None:
        policy.action = policy_update.action
    if policy_update.active is not None:
        policy.active = policy_update.active
    
    await db.commit()
    await db.refresh(policy)
    
    return policy


@router.delete("/{policy_id}")
async def delete_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a policy"""
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id)
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    await db.delete(policy)
    await db.commit()
    
    return {"message": "Policy deleted"}


@router.patch("/{policy_id}/toggle", response_model=PolicyResponse)
async def toggle_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    """Toggle policy active status"""
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id)
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policy.active = not policy.active
    
    await db.commit()
    await db.refresh(policy)
    
    return policy

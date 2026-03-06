"""
Expense Policy Enforcer - FastAPI Application
Hackathon Zero - February 2026
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import expenses, policies, audit

app = FastAPI(
    title="Expense Policy Enforcer",
    description="Automated expense policy validation system",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses.router, prefix="/api/v1/expenses", tags=["expenses"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["policies"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Expense Policy Enforcer API", "version": "1.0.0"}


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "expense-policy-enforcer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

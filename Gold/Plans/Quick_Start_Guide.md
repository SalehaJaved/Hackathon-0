# Quick Start Guide - Expense Policy Enforcer

**For Hackathon Judges & Demo Users**

---

## Option 1: Try Live Demo (Recommended)

If deployed to Railway/Render:

```
URL: https://[your-app].railway.app
```

No login required for demo mode!

---

## Option 2: Run Locally (5 Minutes)

### Prerequisites
- Docker Desktop installed
- Git installed

### Steps

```bash
# 1. Clone repository
git clone https://github.com/[team]/expense-policy-enforcer.git
cd expense-policy-enforcer

# 2. Start all services
docker-compose up --build

# Wait 30 seconds for build...

# 3. Open browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## Quick Demo Flow (2 Minutes)

### Step 1: Dashboard
```
1. Open http://localhost:3000
2. You'll see the dashboard with stats
3. Click "Submit Expense"
```

### Step 2: Submit Expense
```
1. Fill in:
   - Vendor: "Amazon Web Services"
   - Amount: 149.99
   - Date: Today
   - Category: Software & Services
2. Click "Submit Expense"
3. See: "Requires manager approval" (>$100 policy)
```

### Step 3: View in Expenses
```
1. Click "Expenses" in navigation
2. See your expense with "NEEDS REVIEW" badge
3. Click "✓ Approve"
4. Status changes to "APPROVED"
```

### Step 4: Check Policies
```
1. Click "Policies" in navigation
2. See active policies:
   - "Manager Approval for Expenses >$100"
   - "Receipt Required for Expenses >$25"
3. Toggle a policy on/off
```

### Step 5: API Documentation
```
1. Open http://localhost:8000/docs
2. See all REST API endpoints
3. Try "GET /api/v1/expenses" → Execute
4. See JSON response with your expense
```

---

## Test Scenarios

### Scenario 1: Auto-Approved Expense
```
Submit expense with amount = 50.00
Expected: Status = "APPROVED" (under $100 threshold)
```

### Scenario 2: Manager Approval Required
```
Submit expense with amount = 149.99
Expected: Status = "NEEDS REVIEW" (over $100)
```

### Scenario 3: Receipt Upload
```
1. Click "Submit Expense"
2. Upload any image file (JPG/PNG)
3. See OCR processing in action
4. Vendor/amount auto-filled from receipt
```

---

## Troubleshooting

### Frontend won't load
```
Check: Is backend running on port 8000?
Fix: docker-compose ps (both services should be "Up")
```

### API errors in browser console
```
Check: Is backend healthy?
Visit: http://localhost:8000/api/v1/health
Expected: {"status": "healthy"}
```

### Database errors
```
Fix: Delete backend/data/expenses.db and restart
Command: docker-compose down && docker-compose up --build
```

### OCR not working
```
Check: Tesseract installed in Docker container
Logs: docker-compose logs backend | grep -i ocr
```

---

## Key Features to Demo

| Feature | How to Show | Time |
|---------|-------------|------|
| Receipt Upload | Upload sample image | 30s |
| OCR Processing | Show auto-filled form | 20s |
| Policy Violation | Submit $149.99 expense | 20s |
| Approval Workflow | Approve from Expenses page | 20s |
| Audit Log | Check backend logs or DB | 20s |
| Policy Management | Toggle policy on/off | 20s |

**Total Demo Time:** 2-3 minutes

---

## Sample Test Data

### Expense 1: Office Supplies (Auto-Approved)
```
Vendor: Staples
Amount: 45.00
Category: Office Supplies
Date: [Today]
```

### Expense 2: Client Dinner (Needs Review)
```
Vendor: The Capital Grille
Amount: 250.00
Category: Meals
Date: [Today]
```

### Expense 3: Software Subscription (Auto-Approved)
```
Vendor: Adobe Creative Cloud
Amount: 54.99
Category: Software
Date: [Today]
```

---

## API Quick Reference

```bash
# List all expenses
curl http://localhost:8000/api/v1/expenses/

# Get dashboard stats
curl http://localhost:8000/api/v1/expenses/dashboard/stats

# List policies
curl http://localhost:8000/api/v1/policies/

# Submit expense (no receipt)
curl -X POST http://localhost:8000/api/v1/expenses/ \
  -F "vendor=Test Vendor" \
  -F "amount=75.00" \
  -F "date=2026-02-19" \
  -F "category=general"
```

---

## What Judges Should See

✅ **Working Features:**
- Expense submission form
- Receipt upload (optional)
- Policy violation detection
- Manager approval workflow
- Dashboard statistics
- Policy management
- Audit logging

✅ **Technical Highlights:**
- Clean React UI with Tailwind CSS
- FastAPI backend with auto-docs
- Docker Compose deployment
- Async database operations
- OCR integration

---

## Contact for Support

If you encounter issues during judging:

```
Email: team@expense-enforcer.com
GitHub Issues: https://github.com/[team]/expense-policy-enforcer/issues
```

---

**Enjoy the demo! 🚀**

*Built for Hackathon Zero - February 2026*

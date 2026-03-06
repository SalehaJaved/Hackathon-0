# Expense Policy Enforcer - Implementation Plan

**Hackathon Zero Project**  
**Version:** 1.0  
**Status:** Ready for Development  

---

## Executive Summary

An automated expense policy validation system that checks expense submissions against configurable company rules (e.g., "$100 requires manager approval") before processing. Built for SMBs neglected by enterprise solutions like SAP Concur.

**Target:** Working MVP within 48 hours  
**Differentiator:** 1-hour setup, transparent pricing, platform-agnostic  

---

## Problem Statement

| Issue | Impact |
|-------|--------|
| Manual expense review is slow | 5-10 days average reimbursement time |
| Policy violations slip through | Companies lose 5-7% annually to non-compliant expenses |
| Enterprise tools too complex | Weeks of implementation, $10K+/year cost |
| No real-time enforcement | Violations discovered post-payment |

---

## Proposed Solution

**Expense Policy Enforcer** - A lightweight middleware that:
1. Intercepts expense submissions (file upload or API)
2. Extracts data via OCR (vendor, amount, date, category)
3. Validates against configurable policy rules
4. Routes for approval or auto-rejects
5. Logs all actions for audit compliance

---

## Target Audience

| Segment | Characteristics | Why They Need This |
|---------|-----------------|-------------------|
| **Small Businesses** | 10-100 employees, no dedicated finance team | Can't afford Concur, need basic compliance |
| **Startups** | Venture-backed, rapid hiring, expense policies exist but unenforced | Investors demand financial controls |
| **Professional Services** | Law firms, consultancies, agencies | High travel/entertainment spend, billable client expenses |
| **Remote Teams** | Distributed workforce, asynchronous approvals | Need digital-first expense workflows |

---

## Key Features (MVP Scope)

### Phase 1: Core (Hackathon MVP)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Receipt Upload** | Drag-drop or email attachment ingestion | P0 |
| **OCR Processing** | Extract vendor, amount, date, tax from receipts | P0 |
| **Policy Rules Engine** | JSON-based rules (thresholds, categories, approvers) | P0 |
| **Violation Detection** | Auto-flag expenses breaking policies | P0 |
| **Approval Workflow** | Email notifications to managers for review | P0 |
| **Audit Log** | Immutable record of all actions and decisions | P0 |
| **Dashboard** | Simple web UI showing pending/rejected/approved | P1 |

### Phase 2: Post-Hackathon

| Feature | Description |
|---------|-------------|
| Accounting Integration | QuickBooks, Xero sync |
| Multi-currency Support | Auto-convert foreign expenses |
| Corporate Card Integration | Real-time transaction feeds |
| Slack/Teams Notifications | In-app approval requests |
| Mobile App | Receipt capture via phone camera |
| Advanced Analytics | Spend trends, policy violation patterns |

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Expense Policy Enforcer                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────────┐   │
│  │  Input   │───▶│  Processing  │───▶│    Decision Engine  │   │
│  │  Layer   │    │     Layer    │    │                     │   │
│  │          │    │              │    │  ┌───────────────┐  │   │
│  │ • Upload │    │ • OCR        │    │  │ Rules Engine  │  │   │
│  │ • Email  │    │ • Validation │    │  │ • Thresholds  │  │   │
│  │ • API    │    │ • Enrichment │    │  │ • Categories  │  │   │
│  └──────────┘    └──────────────┘    │  │ • Approvers   │  │   │
│                                       │  └───────┬───────┘  │   │
│                                       └──────────┼──────────┘   │
│                                                  ▼              │
│                                       ┌─────────────────────┐   │
│                                       │    Action Layer     │   │
│                                       │                     │   │
│                                       │ • Auto-approve      │   │
│                                       │ • Route for review  │   │
│                                       │ • Reject + notify   │   │
│                                       │ • Log to audit trail│   │
│                                       └─────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Backend** | Python 3.11+ | Rich OCR/NLP libraries, fast prototyping |
| **Web Framework** | FastAPI | Async support, auto docs, lightweight |
| **OCR** | Tesseract + OpenCV | Free, offline-capable, 95%+ accuracy |
| **Database** | SQLite (MVP) → PostgreSQL | Zero-config for hackathon, scalable later |
| **ORM** | SQLAlchemy | Mature, async support |
| **Rules Engine** | pyke or custom JSON | Lightweight, no JVM dependency |
| **Frontend** | React + Tailwind CSS | Fast UI development, responsive |
| **Email** | SMTP (SendGrid free tier) | Reliable, hackathon-friendly |
| **File Storage** | Local filesystem (MVP) → S3 | Simple for demo, cloud-ready |
| **Deployment** | Docker + docker-compose | Portable, reproducible |

---

## Data Model

### `expenses` Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Submitter reference |
| vendor | VARCHAR | Merchant name |
| amount | DECIMAL | Expense amount |
| currency | VARCHAR | Default USD |
| date | DATE | Transaction date |
| category | VARCHAR | Auto-classified (meals, travel, etc.) |
| receipt_path | VARCHAR | File system path |
| ocr_data | JSON | Raw OCR extraction |
| status | ENUM | pending, approved, rejected, needs_review |
| created_at | TIMESTAMP | Submission time |

### `policies` Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR | Rule name (e.g., "Manager Approval >$100") |
| condition_type | ENUM | amount_threshold, category_restriction, vendor_block |
| condition_json | JSON | Rule parameters |
| action | ENUM | auto_approve, require_approval, auto_reject |
| approver_id | UUID | Manager for approvals |
| active | BOOLEAN | Enable/disable toggle |

### `audit_log` Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| expense_id | UUID | Related expense |
| action | VARCHAR | submitted, approved, rejected, flagged |
| actor_id | UUID | User or system |
| reason | TEXT | Decision rationale |
| timestamp | TIMESTAMP | Action time |

---

## Policy Rules Schema

```json
{
  "rules": [
    {
      "id": "rule_001",
      "name": "Manager Approval for Expenses >$100",
      "condition": {
        "type": "amount_threshold",
        "operator": "greater_than",
        "value": 100,
        "currency": "USD"
      },
      "action": "require_approval",
      "approver_role": "manager"
    },
    {
      "id": "rule_002",
      "name": "Auto-reject Gambling",
      "condition": {
        "type": "category_restriction",
        "blocked_categories": ["gambling", "casinos"]
      },
      "action": "auto_reject"
    },
    {
      "id": "rule_003",
      "name": "Meals Per Diem $50",
      "condition": {
        "type": "category_threshold",
        "category": "meals",
        "value": 50
      },
      "action": "require_approval"
    },
    {
      "id": "rule_004",
      "name": "Auto-approve Office Supplies <$25",
      "condition": {
        "type": "category_amount",
        "category": "office_supplies",
        "operator": "less_than",
        "value": 25
      },
      "action": "auto_approve"
    }
  ]
}
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/expenses` | Submit new expense (multipart form) |
| GET | `/api/expenses` | List expenses (filterable) |
| GET | `/api/expenses/{id}` | Get expense details |
| POST | `/api/expenses/{id}/approve` | Approve expense |
| POST | `/api/expenses/{id}/reject` | Reject expense |
| GET | `/api/policies` | List all policies |
| POST | `/api/policies` | Create new policy |
| PUT | `/api/policies/{id}` | Update policy |
| DELETE | `/api/policies/{id}` | Delete policy |
| GET | `/api/audit-log` | Get audit trail |
| GET | `/api/dashboard/stats` | Dashboard metrics |

---

## Implementation Timeline (48 Hours)

### Day 1

| Time | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 0-2h | Project setup, repo structure | All | Working scaffold |
| 2-4h | Database models + migrations | Backend | SQLite schema |
| 4-6h | OCR pipeline (Tesseract integration) | Backend | Receipt → JSON |
| 6-8h | Policy rules engine (JSON parser) | Backend | Rule evaluation |
| 8-10h | Expense submission API | Backend | POST /expenses working |
| 10-12h | Basic frontend (upload form) | Frontend | Upload UI |

### Day 2

| Time | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 12-14h | Approval workflow (email notifications) | Backend | Email integration |
| 14-16h | Dashboard (pending/approved/rejected) | Frontend | Stats + list views |
| 16-18h | Audit logging + export | Backend | CSV/PDF export |
| 18-20h | Policy management UI | Frontend | CRUD for policies |
| 20-22h | Integration testing | All | End-to-end flow |
| 22-24h | Demo prep, bug fixes | All | Pitch-ready demo |

---

## Sample Policy Configuration

Based on your existing `Company_Handbook.md`:

```json
{
  "company_name": "Hackathon Zero Inc.",
  "policies": [
    {
      "id": "handbook_001",
      "name": "Manager Approval Rule (Company Handbook)",
      "description": "Any expense above $100 requires prior approval from a manager",
      "condition": {
        "type": "amount_threshold",
        "operator": "greater_than",
        "value": 100,
        "currency": "USD"
      },
      "action": "require_approval",
      "approver_role": "manager",
      "source": "Company_Handbook.md"
    },
    {
      "id": "handbook_002",
      "name": "Receipt Requirement",
      "description": "Submit expense reports with receipts for reimbursement",
      "condition": {
        "type": "receipt_required",
        "threshold": 25
      },
      "action": "require_receipt",
      "source": "Company_Handbook.md"
    }
  ]
}
```

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OCR accuracy <90% | High | Fallback to manual entry form; highlight low-confidence fields |
| Email delivery failures | Medium | Use SendGrid free tier; log failures; retry queue |
| Scope creep | High | Strict MVP feature freeze after 12h |
| Integration complexity | Medium | Defer accounting integrations to Phase 2 |
| Security concerns | High | Input sanitization, parameterized queries, no secrets in code |

---

## Success Metrics (Demo Criteria)

| Metric | Target |
|--------|--------|
| Receipt upload → decision | <30 seconds |
| OCR accuracy on clean receipts | >90% |
| Policy rule evaluation | <100ms |
| End-to-end workflow demo | Upload → Flag → Approve → Log |
| Code quality | Passes linting, basic tests |

---

## Future Roadmap

| Quarter | Milestone |
|---------|-----------|
| Q1 2026 | Multi-currency, QuickBooks integration |
| Q2 2026 | Mobile app (iOS/Android), Slack bot |
| Q3 2026 | Advanced analytics, spend insights |
| Q4 2026 | SOC 2 compliance, enterprise SSO |

---

## Repository Structure

```
expense-policy-enforcer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # DB connection
│   │   ├── ocr/
│   │   │   ├── __init__.py
│   │   │   └── processor.py     # Tesseract integration
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   └── engine.py        # Policy evaluation
│   │   ├── workflows/
│   │   │   ├── __init__.py
│   │   │   └── approvals.py     # Email notifications
│   │   └── routes/
│   │       ├── expenses.py
│   │       ├── policies.py
│   │       └── audit.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── policies/
│   └── default_policies.json
└── README.md
```

---

## Getting Started (Development)

```bash
# Clone and setup
git clone <repo>
cd expense-policy-enforcer

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker (alternative)
docker-compose up --build
```

---

## Demo Script

1. **Upload Receipt**: Drag-drop a sample receipt image
2. **Show OCR Extraction**: Display auto-extracted vendor, amount, date
3. **Policy Evaluation**: Show rule matching ("$100 approval required")
4. **Approval Flow**: Manager receives email, clicks approve
5. **Audit Log**: Export CSV showing full trail
6. **Policy Management**: Create new rule in UI, test immediately

---

*Prepared for Hackathon Zero • Expense Policy Enforcer v1.0*

# Expense Policy Enforcer - Technical Architecture

**Hackathon Zero** | **System Design Document**  
**Version:** 1.0 | **Last Updated:** 2026-02-19

---

## System Overview

### Architecture Style
**Layered Monolith with Event-Driven Extensions**

Chosen for hackathon velocity while maintaining escape hatches for microservices evolution.

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Separation of Concerns** | Clear boundaries: API → Service → Repository |
| **Single Source of Truth** | SQLite (MVP) → PostgreSQL (Production) |
| **Async-First** | FastAPI async endpoints, background task queues |
| **Fail Gracefully** | OCR fallbacks, circuit breakers, retry logic |
| **Security by Default** | Input validation, parameterized queries, JWT auth |

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Expense Policy Enforcer                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         PRESENTATION LAYER                        │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │   React SPA     │  │   Swagger UI    │  │   Webhooks      │   │   │
│  │  │   (Frontend)    │  │   (API Docs)    │  │   (Integrations)│   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│                                   ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                          API GATEWAY                              │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │              FastAPI Application (main.py)                 │  │   │
│  │  │  • Request Validation  • Authentication  • Rate Limiting   │  │   │
│  │  └────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│                                   ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        BUSINESS LOGIC LAYER                       │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │   │
│  │  │   Expense    │ │    Policy    │ │   Workflow   │ │  Audit   │ │   │
│  │  │   Service    │ │   Service    │ │   Service    │ │  Service │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────┘ │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│                                   ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        PROCESSING LAYER                           │   │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌──────────────┐  │   │
│  │  │   OCR Pipeline    │  │   Rules Engine    │  │  Notification│  │   │
│  │  │  (Tesseract/OpenCV)│  │  (JSON/PyKE)     │  │   (SendGrid) │  │   │
│  │  └───────────────────┘  └───────────────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│                                   ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         DATA ACCESS LAYER                         │   │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌──────────────┐  │   │
│  │  │   Repository      │  │   Unit of Work    │  │   Migrations │  │   │
│  │  │   (SQLAlchemy)    │  │   (Transactions)  │  │   (Alembic)  │  │   │
│  │  └───────────────────┘  └───────────────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│                                   ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                          DATA LAYER                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │   SQLite     │  │   File       │  │   Cache              │   │   │
│  │  │   Database   │  │   Storage    │  │   (Redis - Future)   │   │   │
│  │  │   (MVP)      │  │   (Receipts) │  │                      │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Diagram Description

### Component Interaction Flow

```
User Action Flow:
─────────────────

1. EXPENSE SUBMISSION
   ┌────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
   │  User  │────▶│ Frontend │────▶│ API Layer │────▶│ Expense  │────▶│ Database │
   │(Browser)│    │(React)   │     │(FastAPI)  │     │ Service  │     │(SQLite)  │
   └────────┘     └──────────┘     └───────────┘     └──────────┘     └──────────┘
                      │                  │                  │
                      │                  ▼                  │
                      │           ┌───────────┐            │
                      │           │   OCR     │            │
                      │           │  Pipeline │            │
                      │           └───────────┘            │
                      │                  │                  │
                      │                  ▼                  │
                      │           ┌───────────┐            │
                      └───────────│  Rules    │◀───────────┘
                                   │  Engine   │
                                   └───────────┘
                                         │
                                         ▼
                                   ┌───────────┐
                                   │ Workflow  │
                                   │  Service  │
                                   └───────────┘
                                         │
                                         ▼
                                   ┌───────────┐
                                   │  Email    │
                                   │(SendGrid) │
                                   └───────────┘


2. APPROVAL WORKFLOW
   ┌─────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
   │ Manager │────▶│   Email  │────▶│ API Layer │────▶│ Workflow │────▶│ Database │
   │(Browser)│     │(Click)   │     │(FastAPI)  │     │ Service  │     │(Update)  │
   └─────────┘     └──────────┘     └───────────┘     └──────────┘     └──────────┘
                                           │                  │
                                           ▼                  ▼
                                     ┌───────────┐     ┌───────────┐
                                     │   Audit   │     │   Audit   │
                                     │   Log     │     │  Export   │
                                     └───────────┘     └───────────┘
```

### Deployment Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION DEPLOYMENT                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      Cloud Provider (Railway/Render)             │    │
│  │                                                                   │    │
│  │  ┌─────────────────────┐         ┌─────────────────────┐         │    │
│  │  │   Backend Container │         │  Frontend Container │         │    │
│  │  │   (FastAPI + Gunicorn)│        │  (React + Nginx)    │         │    │
│  │  │   Port: 8000        │         │  Port: 80           │         │    │
│  │  │                     │         │                     │         │    │
│  │  │  ┌───────────────┐  │         │  ┌───────────────┐  │         │    │
│  │  │  │ OCR Worker    │  │         │  │ Static Assets │  │         │    │
│  │  │  │ (Background)  │  │         │  │ (CDN Cached)  │  │         │    │
│  │  │  └───────────────┘  │         │  └───────────────┘  │         │    │
│  │  └──────────┬──────────┘         └──────────┬──────────┘         │    │
│  │             │                               │                     │    │
│  │             └───────────────┬───────────────┘                     │    │
│  │                             │                                     │    │
│  │                             ▼                                     │    │
│  │                  ┌─────────────────────┐                          │    │
│  │                  │  PostgreSQL Database│                          │    │
│  │                  │  (Managed Service)  │                          │    │
│  │                  │  Port: 5432         │                          │    │
│  │                  └─────────────────────┘                          │    │
│  │                                                                   │    │
│  │  ┌─────────────────────┐         ┌─────────────────────┐         │    │
│  │  │   File Storage      │         │   External Services │         │    │
│  │  │   (AWS S3 / R2)     │         │   • SendGrid (Email)│         │    │
│  │  │   Receipts Bucket   │         │   • Tesseract (OCR) │         │    │
│  │  └─────────────────────┘         └─────────────────────┘         │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  INTERNET ──────▶ Load Balancer ──────▶ Application                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│      users          │       │     expenses        │       │     policies        │
├─────────────────────┤       ├─────────────────────┤       ├─────────────────────┤
│ id (UUID, PK)       │◀──────│ user_id (UUID, FK)  │       │ id (UUID, PK)       │
│ email (VARCHAR)     │       │ id (UUID, PK)       │       │ name (VARCHAR)      │
│ name (VARCHAR)      │       │ vendor (VARCHAR)    │       │ condition_type      │
│ role (ENUM)         │       │ amount (DECIMAL)    │       │ condition_json      │
│ department (VARCHAR)│       │ currency (VARCHAR)  │       │ action (ENUM)       │
│ manager_id (UUID)   │       │ date (DATE)         │       │ approver_id (UUID)  │
│ created_at (TIMESTAMP)│     │ category (VARCHAR)  │       │ active (BOOLEAN)    │
│ updated_at (TIMESTAMP)│     │ receipt_path (VARCHAR)│     │ created_at (TIMESTAMP)│
└─────────────────────┘       │ ocr_data (JSON)     │       │ updated_at (TIMESTAMP)│
         │                    │ status (ENUM)       │       └─────────────────────┘
         │                    │ policy_violations   │                  │
         │                    │   (JSON)            │                  │
         │                    │ created_at (TIMESTAMP)│                │
         │                    │ updated_at (TIMESTAMP)│                │
         │                    └──────────┬──────────┘                  │
         │                               │                              │
         │                               ▼                              │
         │                    ┌─────────────────────┐                  │
         │                    │   audit_log         │                  │
         │                    ├─────────────────────┤                  │
         └───────────────────▶│ id (UUID, PK)       │◀─────────────────┘
                              │ expense_id (UUID, FK)│
                              │ policy_id (UUID, FK) │
                              │ user_id (UUID, FK)   │
                              │ action (VARCHAR)     │
                              │ previous_value (JSON)│
                              │ new_value (JSON)     │
                              │ reason (TEXT)        │
                              │ ip_address (VARCHAR) │
                              │ timestamp (TIMESTAMP)│
                              └─────────────────────┘
```

### Table Definitions

#### `users` Table
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    role            ENUM('submitter', 'manager', 'admin', 'finance') NOT NULL,
    department      VARCHAR(100),
    manager_id      UUID REFERENCES users(id),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_manager ON users(manager_id);
```

#### `expenses` Table
```sql
CREATE TABLE expenses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES users(id) ON DELETE CASCADE,
    vendor              VARCHAR(255) NOT NULL,
    amount              DECIMAL(10, 2) NOT NULL,
    currency            VARCHAR(3) DEFAULT 'USD',
    date                DATE NOT NULL,
    category            VARCHAR(50),
    receipt_path        VARCHAR(500),
    receipt_url         VARCHAR(500),
    ocr_data            JSONB,
    status              ENUM('pending', 'approved', 'rejected', 'needs_review') DEFAULT 'pending',
    policy_violations   JSONB,
    notes               TEXT,
    approved_by         UUID REFERENCES users(id),
    approved_at         TIMESTAMP WITH TIME ZONE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_status ON expenses(status);
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_amount ON expenses(amount);
```

#### `policies` Table
```sql
CREATE TABLE policies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    condition_type  ENUM('amount_threshold', 'category_restriction', 'vendor_block', 
                         'category_threshold', 'receipt_required', 'custom') NOT NULL,
    condition_json  JSONB NOT NULL,
    action          ENUM('auto_approve', 'require_approval', 'auto_reject', 'flag_for_review') NOT NULL,
    approver_role   VARCHAR(50),
    priority        INTEGER DEFAULT 0,
    active          BOOLEAN DEFAULT TRUE,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policies_active ON policies(active);
CREATE INDEX idx_policies_type ON policies(condition_type);
```

#### `audit_log` Table
```sql
CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expense_id      UUID REFERENCES expenses(id) ON DELETE CASCADE,
    policy_id       UUID REFERENCES policies(id),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(50) NOT NULL,
    previous_value  JSONB,
    new_value       JSONB,
    reason          TEXT,
    ip_address      VARCHAR(45),
    user_agent      VARCHAR(255),
    timestamp       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_expense ON audit_log(expense_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_action ON audit_log(action);
```

#### `notifications` Table
```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expense_id      UUID REFERENCES expenses(id) ON DELETE CASCADE,
    recipient_id    UUID REFERENCES users(id),
    recipient_email VARCHAR(255),
    type            ENUM('email', 'slack', 'in_app') NOT NULL,
    subject         VARCHAR(255),
    body            TEXT NOT NULL,
    status          ENUM('pending', 'sent', 'failed', 'delivered') DEFAULT 'pending',
    sent_at         TIMESTAMP WITH TIME ZONE,
    error_message   TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_recipient ON notifications(recipient_id);
CREATE INDEX idx_notifications_status ON notifications(status);
```

---

## API Structure

### RESTful API Design

```
BASE URL: /api/v1
```

### Endpoint Groups

#### 1. Authentication & Users
```
POST   /api/v1/auth/register          # Register new user
POST   /api/v1/auth/login             # Login (returns JWT)
POST   /api/v1/auth/logout            # Logout (invalidate token)
POST   /api/v1/auth/refresh           # Refresh JWT token
POST   /api/v1/auth/forgot-password   # Request password reset
POST   /api/v1/auth/reset-password    # Reset password with token

GET    /api/v1/users                  # List users (admin only)
GET    /api/v1/users/{id}             # Get user details
PUT    /api/v1/users/{id}             # Update user
DELETE /api/v1/users/{id}             # Delete user (admin only)
GET    /api/v1/users/me               # Get current user
```

#### 2. Expenses
```
POST   /api/v1/expenses               # Submit new expense
GET    /api/v1/expenses               # List expenses (filterable)
GET    /api/v1/expenses/{id}          # Get expense details
PUT    /api/v1/expenses/{id}          # Update expense
DELETE /api/v1/expenses/{id}          # Delete expense

POST   /api/v1/expenses/{id}/approve  # Approve expense
POST   /api/v1/expenses/{id}/reject   # Reject expense
POST   /api/v1/expenses/{id}/request-info  # Request more information

GET    /api/v1/expenses/{id}/audit    # Get audit trail for expense
GET    /api/v1/expenses/{id}/receipt  # Download receipt file
PUT    /api/v1/expenses/{id}/receipt  # Upload/replace receipt

# Bulk Operations
POST   /api/v1/expenses/bulk          # Submit multiple expenses
POST   /api/v1/expenses/bulk/approve  # Bulk approve (manager)
POST   /api/v1/expenses/export        # Export to CSV/PDF
```

#### 3. Policies
```
POST   /api/v1/policies               # Create new policy
GET    /api/v1/policies               # List all policies
GET    /api/v1/policies/{id}          # Get policy details
PUT    /api/v1/policies/{id}          # Update policy
DELETE /api/v1/policies/{id}          # Delete policy
PATCH  /api/v1/policies/{id}/toggle   # Enable/disable policy

POST   /api/v1/policies/validate      # Test policy against sample data
GET    /api/v1/policies/templates     # Get pre-built policy templates
POST   /api/v1/policies/import        # Import policies from JSON
GET    /api/v1/policies/export        # Export policies to JSON
```

#### 4. Audit & Reporting
```
GET    /api/v1/audit-log              # Get audit trail (filterable)
GET    /api/v1/audit-log/{id}         # Get specific audit entry
GET    /api/v1/audit-log/export       # Export audit log (CSV)

GET    /api/v1/reports/spending       # Spending summary report
GET    /api/v1/reports/violations     # Policy violation report
GET    /api/v1/reports/pending        # Pending approvals report
GET    /api/v1/reports/dashboard      # Dashboard metrics
```

#### 5. System & Health
```
GET    /api/v1/health                 # Health check
GET    /api/v1/health/ready           # Readiness probe
GET    /api/v1/health/live            # Liveness probe
GET    /api/v1/config                 # Get public configuration
GET    /api/v1/categories             # List expense categories
GET    /api/v1/currencies             # List supported currencies
```

### Request/Response Examples

#### Submit Expense
```http
POST /api/v1/expenses
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

Form Data:
  receipt: <file>
  vendor: "Amazon Web Services"
  amount: 149.99
  date: "2026-02-19"
  category: "software"
  notes: "Monthly cloud infrastructure"
```

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "vendor": "Amazon Web Services",
    "amount": 149.99,
    "currency": "USD",
    "date": "2026-02-19",
    "category": "software",
    "status": "needs_review",
    "policy_violations": [
      {
        "policy_id": "rule_001",
        "policy_name": "Manager Approval for Expenses >$100",
        "reason": "Amount $149.99 exceeds threshold $100.00"
      }
    ],
    "ocr_data": {
      "confidence": 0.96,
      "raw_text": "AMAZON WEB SERVICES\nAmount: $149.99\nDate: Feb 19, 2026"
    },
    "created_at": "2026-02-19T10:30:00Z",
    "updated_at": "2026-02-19T10:30:00Z"
  },
  "message": "Expense submitted successfully. Requires manager approval."
}
```

#### Approve Expense
```http
POST /api/v1/expenses/{id}/approve
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "reason": "Approved - within Q1 infrastructure budget"
}
```

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "approved",
    "approved_by": "770e8400-e29b-41d4-a716-446655440002",
    "approved_at": "2026-02-19T11:45:00Z"
  },
  "message": "Expense approved successfully"
}
```

---

## Deployment Strategy

### Environment Tiers

| Environment | Purpose | Infrastructure | Auto-Deploy |
|-------------|---------|----------------|-------------|
| **Development** | Local development | Docker Compose | Manual |
| **Staging** | Pre-production testing | Railway/Render | On PR merge |
| **Production** | Live application | Railway/Render + CDN | On main merge |

### Docker Configuration

#### Backend Dockerfile
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

# Run with gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### Frontend Dockerfile
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget -q --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose (Development)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/expenses.db
      - SECRET_KEY=${SECRET_KEY}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - ENVIRONMENT=development
    volumes:
      - ./backend:/app
      - ./data:/app/data
      - ./receipts:/app/receipts
    depends_on:
      - ocr-worker

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  ocr-worker:
    build: ./backend
    command: python -m app.workers.ocr_worker
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/expenses.db
    volumes:
      - ./receipts:/app/receipts
    depends_on:
      - backend

  pgadmin:
    image: dpage/pgadmin4
    ports:
      - "5050:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@localhost
      - PGADMIN_DEFAULT_PASSWORD=admin
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=expenses
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

### CI/CD Pipeline (GitHub Actions)

```yaml
name: Deploy

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: pytest backend/tests --cov=backend/app
      - name: Run linter
        run: flake8 backend/app

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t expense-enforcer-backend ./backend
          docker build -t expense-enforcer-frontend ./frontend

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        uses: railwayapp/railway-action@v1
        with:
          api_token: ${{ secrets.RAILWAY_API_TOKEN }}
          environment: staging

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        uses: railwayapp/railway-action@v1
        with:
          api_token: ${{ secrets.RAILWAY_API_TOKEN }}
          environment: production
```

### Production Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐                                                │
│  │   Cloudflare│ (CDN + DDoS Protection)                        │
│  │    CDN      │                                                │
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Railway/Render Platform                     │    │
│  │                                                          │    │
│  │  ┌──────────────────┐    ┌──────────────────┐           │    │
│  │  │   Web Service    │    │   Web Service    │           │    │
│  │  │   (Backend)      │    │   (Frontend)     │           │    │
│  │  │   2x Replicas    │    │   Static + Nginx │           │    │
│  │  │   Auto-scaling   │    │                  │           │    │
│  │  └──────────────────┘    └──────────────────┘           │    │
│  │                                                          │    │
│  │  ┌──────────────────┐    ┌──────────────────┐           │    │
│  │  │  Background      │    │   Managed        │           │    │
│  │  │  Worker (OCR)    │    │   PostgreSQL     │           │    │
│  │  │                  │    │   (10GB)         │           │    │
│  │  └──────────────────┘    └──────────────────┘           │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   AWS S3 / R2    │    │   SendGrid       │                  │
│  │   (Receipts)     │    │   (Email)        │                  │
│  │   5GB Free       │    │   100/day Free   │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

### Authentication & Authorization

#### JWT Token Structure
```json
{
  "sub": "user-uuid",
  "email": "user@company.com",
  "role": "manager",
  "permissions": ["expenses:read", "expenses:write", "expenses:approve"],
  "iat": 1676800000,
  "exp": 1676886400
}
```

#### Role-Based Access Control (RBAC)
```python
ROLES = {
    "submitter": {
        "expenses": ["create", "read:own", "update:own"],
        "policies": ["read"],
    },
    "manager": {
        "expenses": ["create", "read:own", "update:own", "read:team", "approve:team"],
        "policies": ["read"],
        "reports": ["read:team"],
    },
    "finance": {
        "expenses": ["read:all", "update:all", "approve:all", "export"],
        "policies": ["read", "create", "update"],
        "reports": ["read:all", "export"],
        "audit_log": ["read:all", "export"],
    },
    "admin": {
        "expenses": ["*"],
        "policies": ["*"],
        "users": ["*"],
        "reports": ["*"],
        "audit_log": ["*"],
        "config": ["*"],
    },
}
```

### Security Headers
```python
# FastAPI middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### Input Validation
```python
from pydantic import BaseModel, validator, Field
import re

class ExpenseCreate(BaseModel):
    vendor: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, le=100000)
    currency: str = Field(default="USD", regex="^[A-Z]{3}$")
    date: date
    category: str = Field(..., regex="^[a-z_]+$")
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('vendor')
    def sanitize_vendor(cls, v):
        # Remove potential XSS
        return html.escape(v.strip())
```

### SQL Injection Prevention
```python
# ✅ CORRECT: Parameterized queries
expenses = await db.execute(
    "SELECT * FROM expenses WHERE user_id = :user_id AND status = :status",
    {"user_id": user_id, "status": "pending"}
)

# ❌ WRONG: String concatenation (vulnerable)
query = f"SELECT * FROM expenses WHERE user_id = '{user_id}'"
```

### File Upload Security
```python
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_upload(file: UploadFile):
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")
    
    # Check MIME type
    content = await file.read()
    if not magic.from_buffer(content, mime=True).startswith(('image/', 'application/pdf')):
        raise HTTPException(400, "Invalid file content")
    
    # Check size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    # Sanitize filename
    safe_filename = secure_filename(file.filename)
    
    return safe_filename, content
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/expenses")
@limiter.limit("10/minute")
async def create_expense(request: Request, expense: ExpenseCreate):
    ...

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: Credentials):
    ...
```

### Audit Logging
```python
async def log_action(
    db: Session,
    user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: UUID,
    previous_value: dict = None,
    new_value: dict = None,
    reason: str = None,
    request: Request = None
):
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        previous_value=previous_value,
        new_value=new_value,
        reason=reason,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(audit_entry)
    await db.commit()
```

### Secrets Management
```bash
# .env (NEVER commit to git)
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@localhost:5432/expenses
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxx
JWT_EXPIRY_HOURS=24
ENVIRONMENT=production
```

```python
# .env.example (safe to commit)
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite+aiosqlite:///./data/expenses.db
SENDGRID_API_KEY=your-sendgrid-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
JWT_EXPIRY_HOURS=24
ENVIRONMENT=development
```

---

## Scalability Considerations

### Horizontal Scaling Strategy

| Component | Scale-Out Approach | Trigger |
|-----------|-------------------|---------|
| **API Servers** | Add replicas behind load balancer | CPU > 70% |
| **OCR Workers** | Queue-based autoscaling | Queue depth > 100 |
| **Database** | Read replicas for queries | Read latency > 100ms |
| **File Storage** | CDN + Object storage (S3) | Storage > 80% |

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | Prometheus + Grafana |
| OCR Processing Time | < 30s per receipt | Application logs |
| Email Delivery | < 60s | SendGrid webhook |
| Database Query Time | < 50ms | PostgreSQL slow query log |
| Uptime | 99.9% | Uptime monitoring |

---

*Technical Architecture Document v1.0 • Expense Policy Enforcer • Hackathon Zero*

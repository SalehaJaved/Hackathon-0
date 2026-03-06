# Expense Policy Enforcer

**Hackathon Zero Project** | February 2026

Automated expense policy validation system for SMBs.

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and enter directory
cd expense-policy-enforcer

# Start all services
docker-compose up --build

# Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

---

## Features

### MVP Features (Hackathon)
- ✅ Receipt upload with OCR processing
- ✅ Automatic policy violation detection
- ✅ Manager approval workflow
- ✅ Audit logging
- ✅ Dashboard with statistics
- ✅ Policy management

### Default Policies
1. **Manager Approval for Expenses >$100** - Any expense above $100 requires manager approval
2. **Receipt Required for Expenses >$25** - Receipts required for reimbursement

---

## API Endpoints

### Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/expenses/` | Submit new expense |
| GET | `/api/v1/expenses/` | List all expenses |
| GET | `/api/v1/expenses/{id}` | Get expense details |
| POST | `/api/v1/expenses/{id}/approve` | Approve expense |
| POST | `/api/v1/expenses/{id}/reject` | Reject expense |
| GET | `/api/v1/expenses/dashboard/stats` | Dashboard statistics |

### Policies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/policies/` | List all policies |
| POST | `/api/v1/policies/` | Create policy |
| PUT | `/api/v1/policies/{id}` | Update policy |
| PATCH | `/api/v1/policies/{id}/toggle` | Toggle active status |

### Audit
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit/` | List audit logs |
| GET | `/api/v1/audit/stats` | Audit statistics |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| Database | SQLite (MVP) / PostgreSQL (Production) |
| OCR | Tesseract + OpenCV |
| Deployment | Docker + Docker Compose |

---

## Project Structure

```
expense-policy-enforcer/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── ocr/
│   │   │   └── processor.py  # OCR processing
│   │   ├── rules/
│   │   │   └── engine.py     # Policy rules engine
│   │   └── routes/
│   │       ├── expenses.py   # Expense endpoints
│   │       ├── policies.py   # Policy endpoints
│   │       └── audit.py      # Audit endpoints
│   ├── receipts/             # Uploaded receipts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main app component
│   │   ├── components/       # React components
│   │   └── api/
│   │       └── client.js     # API client
│   └── package.json
└── docker-compose.yml
```

---

## Demo Workflow

1. **Submit Expense**: Go to Dashboard → Submit Expense → Upload receipt
2. **OCR Processing**: System extracts vendor, amount, date automatically
3. **Policy Check**: System evaluates against active policies
4. **Approval**: If flagged, manager approves via Expenses page
5. **Audit**: All actions logged in audit trail

---

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### API Testing
Open http://localhost:8000/docs for interactive Swagger UI

---

## Troubleshooting

### OCR Not Working
- Ensure Tesseract is installed and in PATH
- Check `pytesseract.get_tesseract_version()` returns version

### Database Errors
- Delete `backend/data/expenses.db` and restart
- Ensure write permissions on data folder

### Frontend Not Loading
- Check backend is running on port 8000
- Verify proxy config in `frontend/vite.config.js`

---

## License

MIT License - Hackathon Zero 2026

---

## Team

Built by Team [Your Name] for Hackathon Zero

**"From receipt to reimbursement in 60 seconds"**

expense-policy-enforcer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── ocr/
│   │   │   ├── __init__.py
│   │   │   └── processor.py     # Tesseract OCR processing
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   └── engine.py        # Policy rules engine
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── expenses.py      # Expense endpoints
│   │       ├── policies.py      # Policy endpoints
│   │       └── audit.py         # Audit log endpoints
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py
│   ├── receipts/                # Uploaded receipt storage
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ExpenseForm.jsx
│   │   │   ├── ExpenseList.jsx
│   │   │   └── PolicyList.jsx
│   │   └── api/
│   │       └── client.js
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md

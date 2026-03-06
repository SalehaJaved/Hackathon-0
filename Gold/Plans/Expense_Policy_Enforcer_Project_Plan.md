# Expense Policy Enforcer - Hackathon Project Plan

**Hackathon Zero** | **72-Hour Sprint Plan**  
**Version:** 1.0 | **Status:** Ready to Execute

---

## Project Breakdown

### Workstreams

```
Expense Policy Enforcer
│
├── WS1: Backend Development (API, Database, Business Logic)
├── WS2: OCR & Processing Pipeline (Receipt Parsing, Data Extraction)
├── WS3: Rules Engine (Policy Configuration, Evaluation)
├── WS4: Frontend Development (UI, Dashboard, Forms)
├── WS5: DevOps & Deployment (Docker, CI/CD, Hosting)
└── WS6: Testing & Demo Prep (QA, Pitch Deck, Demo Script)
```

### Dependency Map

```
                    ┌─────────────┐
                    │  WS1: Setup │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   ┌───────────┐   ┌───────────┐   ┌───────────┐
   │WS2: OCR   │   │WS3: Rules │   │WS4: Front │
   │ Pipeline  │   │  Engine   │   │   Setup   │
   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                   ┌───────────┐
                   │WS5: Deploy│
                   └─────┬─────┘
                         │
                         ▼
                   ┌───────────┐
                   │WS6: Demo  │
                   └───────────┘
```

---

## Milestones

### Milestone 1: Foundation Complete (Hour 0-12)
**Goal:** Working scaffold with database and basic API

| ID | Task | Priority | Dependencies | Deliverable |
|----|------|----------|--------------|-------------|
| M1-T1 | Initialize Git repo + folder structure | P0 | None | Repository ready |
| M1-T2 | Set up Python virtual environment | P0 | M1-T1 | requirements.txt |
| M1-T3 | Create FastAPI app skeleton | P0 | M1-T2 | main.py with health endpoint |
| M1-T4 | Define SQLAlchemy models (expenses, policies, audit_log) | P0 | M1-T3 | models.py |
| M1-T5 | Create SQLite database + run migrations | P0 | M1-T4 | database.db |
| M1-T6 | Implement POST /api/expenses endpoint | P0 | M1-T5 | Expense submission working |
| M1-T7 | Implement GET /api/expenses endpoint | P1 | M1-T6 | List expenses API |
| M1-T8 | Create React app + basic routing | P1 | M1-T1 | Frontend scaffold |

**Milestone Gate:** Can submit an expense via API and see it in database

---

### Milestone 2: Core Processing (Hour 12-24)
**Goal:** OCR pipeline and rules engine functional

| ID | Task | Priority | Dependencies | Deliverable |
|----|------|----------|--------------|-------------|
| M2-T1 | Integrate Tesseract OCR | P0 | M1-T2 | ocr/processor.py |
| M2-T2 | Build receipt image preprocessing (OpenCV) | P0 | M2-T1 | Enhanced OCR accuracy |
| M2-T3 | Create data extraction logic (vendor, amount, date) | P0 | M2-T2 | Structured JSON output |
| M2-T4 | Design policy rules JSON schema | P0 | M1-T4 | policies/default_policies.json |
| M2-T5 | Implement rules engine parser | P0 | M2-T4 | rules/engine.py |
| M2-T6 | Build rule evaluation function | P0 | M2-T5 | evaluate_expense() working |
| M2-T7 | Connect OCR → Rules → Decision flow | P0 | M2-T3, M2-T6 | End-to-end processing |
| M2-T8 | Create policy CRUD API endpoints | P1 | M2-T4 | POST/PUT/DELETE /api/policies |
| M2-T9 | Build upload form UI component | P1 | M1-T8 | Drag-drop interface |
| M2-T10 | Display OCR results in UI | P1 | M2-T3, M2-T9 | User can see extracted data |

**Milestone Gate:** Upload receipt → Auto-extract data → Evaluate against rules → Show decision

---

### Milestone 3: Workflow & Notifications (Hour 24-36)
**Goal:** Approval workflow and email notifications working

| ID | Task | Priority | Dependencies | Deliverable |
|----|------|----------|--------------|-------------|
| M3-T1 | Set up SendGrid email integration | P0 | M1-T3 | Email service configured |
| M3-T2 | Create approval email template | P0 | M3-T1 | HTML email template |
| M3-T3 | Implement POST /api/expenses/{id}/approve | P0 | M1-T6 | Approve endpoint |
| M3-T4 | Implement POST /api/expenses/{id}/reject | P0 | M1-T6 | Reject endpoint |
| M3-T5 | Build approval notification trigger | P0 | M3-T2, M3-T3 | Email sent on flag |
| M3-T6 | Create audit log middleware | P0 | M1-T4 | All actions logged |
| M3-T7 | Implement GET /api/audit-log | P1 | M3-T6 | Audit trail API |
| M3-T8 | Build expense list view UI | P1 | M2-T9 | Table with status badges |
| M3-T9 | Create expense detail view UI | P1 | M2-T9 | Full expense info display |
| M3-T10 | Add approve/reject buttons in UI | P1 | M3-T8 | Manager can take action |

**Milestone Gate:** Flagged expense triggers email → Manager approves/rejects → Audit logged

---

### Milestone 4: Dashboard & Polish (Hour 36-48)
**Goal:** Complete UI with dashboard and policy management

| ID | Task | Priority | Dependencies | Deliverable |
|----|------|----------|--------------|-------------|
| M4-T1 | Build dashboard stats component | P0 | M3-T8 | Pending/approved/rejected counts |
| M4-T2 | Create policy management UI | P0 | M2-T8 | CRUD interface for policies |
| M4-T3 | Implement audit log export (CSV) | P1 | M3-T7 | Download button |
| M4-T4 | Add expense filtering (status, date, category) | P1 | M3-T8 | Filter dropdowns |
| M4-T5 | Create policy violation alerts UI | P1 | M2-T6 | Visual flags for violations |
| M4-T6 | Style all components (Tailwind) | P1 | M4-T1 to M4-T5 | Polished, consistent UI |
| M4-T7 | Add loading states and error handling | P1 | All UI tasks | Better UX |
| M4-T8 | Implement responsive design | P2 | M4-T6 | Mobile-friendly |

**Milestone Gate:** Full-featured dashboard with all CRUD operations

---

### Milestone 5: Deployment & Testing (Hour 48-60)
**Goal:** Production-ready deployment and QA

| ID | Task | Priority | Dependencies | Deliverable |
|----|------|----------|--------------|-------------|
| M5-T1 | Create Dockerfile for backend | P0 | M1-T3 | backend/Dockerfile |
| M5-T2 | Create Dockerfile for frontend | P0 | M1-T8 | frontend/Dockerfile |
| M5-T3 | Write docker-compose.yml | P0 | M5-T1, M5-T2 | One-command deploy |
| M5-T4 | Deploy to cloud (Railway/Render) | P0 | M5-T3 | Live URL |
| M5-T5 | Write unit tests for OCR module | P1 | M2-T3 | test_ocr.py |
| M5-T6 | Write unit tests for rules engine | P1 | M2-T6 | test_rules.py |
| M5-T7 | Write integration tests (API) | P1 | M1-T6 | test_api.py |
| M5-T8 | Perform end-to-end testing | P0 | M5-T4 | Test report |
| M5-T9 | Fix critical bugs | P0 | M5-T8 | Stable build |
| M5-T10 | Security review (input sanitization, SQL injection) | P0 | All backend | Security checklist |

**Milestone Gate:** Deployed, tested, and stable application

---

### Milestone 6: Demo Preparation (Hour 60-72)
**Goal:** Pitch-ready demo and documentation

| ID | Task | Priority | Dependencies | Deliverable |
|----|------|----------|--------------|-------------|
| M6-T1 | Write README.md | P0 | M5-T4 | Project documentation |
| M6-T2 | Create pitch deck (5 slides) | P0 | None | Problem, Solution, Demo, Market, Ask |
| M6-T3 | Prepare sample receipts for demo | P0 | None | 3-5 test images |
| M6-T4 | Rehearse demo script (5 min) | P0 | M6-T2, M6-T3 | Smooth presentation |
| M6-T5 | Record backup demo video | P1 | M6-T4 | 3-min video fallback |
| M6-T6 | Create project showcase page | P1 | M5-T4 | Live demo link |
| M6-T7 | Prepare Q&A talking points | P1 | M6-T2 | Anticipate judge questions |
| M6-T8 | Final polish (typos, UI glitches) | P1 | M5-T9 | Professional presentation |

**Milestone Gate:** Confident, rehearsed demo ready for judges

---

## Task Allocation

### Recommended Team Roles (3-4 Person Team)

| Role | Responsibilities | Tasks |
|------|------------------|-------|
| **Backend Lead** | API, Database, Business Logic | M1-T3 to M1-T7, M2-T8, M3-T3 to M3-T7, M5-T5 to M5-T7, M5-T10 |
| **ML/OCR Engineer** | OCR Pipeline, Data Extraction | M2-T1 to M2-T7, M5-T5 |
| **Frontend Lead** | UI Components, Dashboard, Styling | M1-T8, M2-T9 to M2-T10, M3-T8 to M3-T10, M4-T1 to M4-T8 |
| **DevOps/PM** | Deployment, Testing Coordination, Demo Prep | M1-T1 to M1-T2, M5-T1 to M5-T4, M5-T8 to M5-T9, M6-T1 to M6-T8 |

### 2-Person Team Adjustment

| Role | Responsibilities |
|------|------------------|
| **Full-Stack Dev 1** | Backend + OCR + DevOps (M1, M2, M3, M5) |
| **Full-Stack Dev 2** | Frontend + Testing + Demo (M1-T8, M2-T9/10, M3-T8/9/10, M4, M6) |

### 4-Person Team (Ideal)

| Person | Primary Focus | Secondary Support |
|--------|---------------|-------------------|
| **Person A** | Backend API (WS1) | DevOps (WS5) |
| **Person B** | OCR Pipeline (WS2) | Rules Engine (WS3) |
| **Person C** | Frontend UI (WS4) | Testing (WS6) |
| **Person D** | DevOps + Testing (WS5, WS6) | Demo Prep (WS6) |

---

## Estimated Timeline

### 72-Hour Schedule

```
HOUR 0         HOUR 12        HOUR 24        HOUR 36        HOUR 48        HOUR 60        HOUR 72
 │              │              │              │              │              │              │
 ▼              ▼              ▼              ▼              ▼              ▼              │
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│  MILESTONE 1 │  MILESTONE 2 │  MILESTONE 3 │  MILESTONE 4 │  MILESTONE 5 │  MILESTONE 6 │
│  Foundation  │   Core OCR   │   Workflow   │  Dashboard   │   Deploy &   │    Demo      │
│              │   & Rules    │   & Email    │   & Polish   │    Test      │   Prep       │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
     P0: 8 tasks     P0: 7 tasks     P0: 6 tasks     P0: 2 tasks     P0: 6 tasks     P0: 4 tasks
     P1: 3 tasks     P1: 3 tasks     P1: 4 tasks     P1: 6 tasks     P1: 4 tasks     P1: 4 tasks
```

### Daily Checkpoints

| Day | Focus | End-of-Day Goal |
|-----|-------|-----------------|
| **Day 1** | Setup + Core API | Expense submission working, database populated |
| **Day 2** | OCR + Rules + Workflow | Upload → Extract → Evaluate → Flag working |
| **Day 3** | Polish + Deploy + Demo | Live URL, rehearsed pitch, bug-free demo |

### Hour-by-Hour Breakdown (First 24 Hours)

| Hour | Task | Owner | Status |
|------|------|-------|--------|
| 0-1 | Git repo, folder structure, README scaffold | All | ☐ |
| 1-2 | Python venv, requirements.txt, FastAPI skeleton | Backend | ☐ |
| 2-4 | SQLAlchemy models (expenses, policies, audit_log) | Backend | ☐ |
| 4-5 | SQLite database + migrations | Backend | ☐ |
| 5-7 | POST /api/expenses endpoint | Backend | ☐ |
| 7-8 | GET /api/expenses endpoint | Backend | ☐ |
| 8-9 | React app setup + routing | Frontend | ☐ |
| 9-12 | Tesseract integration + preprocessing | OCR | ☐ |
| 12-15 | Data extraction (vendor, amount, date) | OCR | ☐ |
| 15-18 | Policy rules schema + parser | Rules | ☐ |
| 18-21 | Rule evaluation engine | Rules | ☐ |
| 21-24 | Connect OCR → Rules → Decision | All | ☐ |

---

## Risk Mitigation

### Risk Register

| Risk | Probability | Impact | Mitigation Strategy | Owner |
|------|-------------|--------|---------------------|-------|
| **OCR accuracy <85%** | Medium | High | Fallback to manual entry form; pre-process images with OpenCV enhancement | OCR Engineer |
| **Tesseract installation issues** | Medium | High | Use Docker with pre-built Tesseract image; have Google Vision API as backup | DevOps |
| **Scope creep** | High | High | Feature freeze at Hour 24; move nice-to-haves to Phase 2 backlog | PM |
| **Email delivery failures** | Medium | Medium | Use SendGrid sandbox mode; log emails locally; show in-app notifications as fallback | Backend |
| **Frontend-Backend integration bugs** | Medium | Medium | Define API contracts early (schemas.py); use Swagger docs for testing | All |
| **Deployment platform issues** | Low | High | Have local demo ready; record backup video; test deployment at Hour 36 | DevOps |
| **Team burnout** | Medium | Medium | Enforce 6-hour sleep minimum; rotate tasks; order food to workspace | PM |
| **Git merge conflicts** | Medium | Low | Assign clear file ownership; merge to main branch every 6 hours | All |
| **Database corruption** | Low | High | Hourly database backups; use SQLite for simplicity | Backend |
| **Demo environment failure** | Medium | High | Record video backup at Hour 66; have screenshots ready; test on multiple browsers | PM |

### Contingency Plans

#### Plan B: OCR Fails
- Skip auto-extraction
- Build manual entry form with pre-filled defaults
- Demo focuses on rules engine and workflow

#### Plan C: Deployment Fails
- Run demo locally on laptop
- Use ngrok for temporary public URL
- Have recorded video as final backup

#### Plan D: Team Member Drops
- Cross-train on critical paths (OCR + Backend)
- Reduce scope: skip policy CRUD UI, use JSON config
- Focus on single end-to-end flow that works perfectly

---

## Success Criteria

### Must-Have (Demo-Ready)
- [ ] Upload receipt image
- [ ] Display OCR-extracted data
- [ ] Show policy violation flag
- [ ] Approve/reject action
- [ ] View audit log

### Should-Have (Competitive)
- [ ] Dashboard with stats
- [ ] Policy management UI
- [ ] Email notifications
- [ ] CSV export
- [ ] Responsive design

### Nice-to-Have (Judges Impressed)
- [ ] Multi-currency support
- [ ] Slack notifications
- [ ] Advanced analytics chart
- [ ] Mobile app preview
- [ ] QuickBooks integration preview

---

## Resource Checklist

### Development Tools
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Tesseract OCR installed (or Docker image)
- [ ] Git configured
- [ ] VS Code / IDE ready

### Accounts (Free Tiers)
- [ ] GitHub repository created
- [ ] SendGrid account (100 emails/day free)
- [ ] Railway/Render account for deployment
- [ ] Figma (optional, for UI mockups)

### Sample Data
- [ ] 5-10 receipt images (various vendors, amounts)
- [ ] Sample policy configurations
- [ ] Test user accounts (submitter, manager, admin)

---

## Communication Plan

### During Hackathon

| Channel | Purpose |
|---------|---------|
| **Discord/Slack** | Quick questions, progress updates |
| **GitHub Issues** | Task tracking, bug reports |
| **In-Person** | Pair programming, design decisions |

### Check-In Schedule

| Time | Meeting | Duration |
|------|---------|----------|
| Hour 0 | Kickoff + task assignment | 30 min |
| Hour 12 | Milestone 1 review | 15 min |
| Hour 24 | Milestone 2 review + pivot if needed | 30 min |
| Hour 36 | Milestone 3 review | 15 min |
| Hour 48 | Milestone 4 review + deployment test | 30 min |
| Hour 60 | Demo rehearsal 1 | 30 min |
| Hour 66 | Demo rehearsal 2 (final) | 30 min |
| Hour 70 | Rest + polish | - |
| Hour 72 | Submit + celebrate | - |

---

## Post-Hackathon Roadmap

| Phase | Timeline | Goals |
|-------|----------|-------|
| **Phase 1** | Week 1-2 | Fix bugs from hackathon feedback, improve OCR accuracy |
| **Phase 2** | Week 3-4 | Add QuickBooks/Xero integration, multi-currency |
| **Phase 3** | Month 2 | Mobile app (React Native), Slack bot |
| **Phase 4** | Month 3 | Advanced analytics, team collaboration features |
| **Phase 5** | Month 4-6 | SOC 2 compliance, enterprise SSO, white-label option |

---

*Prepared for Hackathon Zero • Expense Policy Enforcer Project Plan v1.0*

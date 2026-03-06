# Expense Policy Enforcer - UI/UX Design Document

**Hackathon Zero** | **Design Specification**  
**Version:** 1.0 | **Last Updated:** 2026-02-19

---

## Design Principles

### Core Philosophy
**"Clarity Over Cleverness"**

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Simplicity** | Reduce cognitive load | One primary action per screen |
| **Transparency** | Show system status | Real-time feedback on all actions |
| **Forgiveness** | Allow easy recovery | Undo actions, clear error messages |
| **Consistency** | Predictable patterns | Reusable components, standard icons |
| **Accessibility** | Inclusive design | WCAG 2.1 AA compliance |

### Design Goals

1. **Submit expense in < 60 seconds**
2. **Manager approval in < 30 seconds**
3. **Zero training required**
4. **Mobile-responsive from day one**

---

## User Journey

### Persona 1: Sarah (Employee submitting expenses)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SARAH'S EXPENSE SUBMISSION JOURNEY                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. AWARENESS                                                            │
│     ┌──────────┐                                                         │
│     │  Email   │ "You have a new expense to submit for reimbursement"   │
│     │ Reminder │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  2. LOGIN                                                                │
│     ┌──────────┐                                                         │
│     │  Login   │ Email + Password (or SSO)                              │
│     │  Screen  │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  3. DASHBOARD                                                            │
│     ┌──────────┐                                                         │
│     │ Overview │ "3 expenses pending" • "Submit New Expense" button     │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  4. UPLOAD RECEIPT                                                       │
│     ┌──────────┐                                                         │
│     │  Upload  │ Drag & drop receipt image                              │
│     │  Screen  │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  5. REVIEW OCR DATA                                                      │
│     ┌──────────┐                                                         │
│     │  Review  │ Auto-filled: Vendor, Amount, Date ✓                    │
│     │  Screen  │ Edit if needed                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  6. POLICY CHECK                                                         │
│     ┌──────────┐                                                         │
│     │  Status  │ ⚠️ "Requires manager approval (>$100)"                 │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  7. CONFIRMATION                                                         │
│     ┌──────────┐                                                         │
│     │ Success  │ ✓ "Expense submitted! Manager notified."               │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  8. TRACKING                                                             │
│     ┌──────────┐                                                         │
│     │  Status  │ Email notification when approved                       │
│     │  Updates │                                                         │
│     └──────────┘                                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Persona 2: Mike (Manager approving expenses)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MIKE'S APPROVAL WORKFLOW JOURNEY                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. NOTIFICATION                                                         │
│     ┌──────────┐                                                         │
│     │  Email   │ "2 expenses awaiting your approval"                    │
│     │  Alert   │ [View Pending] button                                  │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  2. PENDING LIST                                                         │
│     ┌──────────┐                                                         │
│     │  Queue   │ Table: Employee, Vendor, Amount, Status                │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  3. REVIEW EXPENSE                                                       │
│     ┌──────────┐                                                         │
│     │  Detail  │ Receipt image + OCR data + Policy violations           │
│     │  View    │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  4. DECISION                                                             │
│     ┌──────────┐                                                         │
│     │  Action  │ [Approve] or [Reject] + optional comment               │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  5. CONFIRMATION                                                         │
│     ┌──────────┐                                                         │
│     │ Success  │ ✓ "Expense approved. Employee notified."               │
│     │          │                                                         │
│     └──────────┘                                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Persona 3: Lisa (Finance admin managing policies)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LISA'S POLICY MANAGEMENT JOURNEY                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. DASHBOARD                                                            │
│     ┌──────────┐                                                         │
│     │  Admin   │ "15 violations this week" • "5 active policies"        │
│     │  Overview│                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  2. POLICY LIST                                                          │
│     ┌──────────┐                                                         │
│     │  List    │ All policies with status (Active/Inactive)             │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  3. CREATE/EDIT                                                          │
│     ┌──────────┐                                                         │
│     │  Editor  │ Rule builder: Condition + Action                       │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  4. TEST POLICY                                                          │
│     ┌──────────┐                                                         │
│     │ Preview  │ "If amount > $100 → Require approval" ✓                │
│     │          │                                                         │
│     └──────────┘                                                         │
│           │                                                              │
│           ▼                                                              │
│  5. AUDIT EXPORT                                                         │
│     ┌──────────┐                                                         │
│     │  Report  │ Download CSV of all policy decisions                   │
│     │          │                                                         │
│     └──────────┘                                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Main Screens

### Screen Inventory

| ID | Screen Name | User Role | Priority |
|----|-------------|-----------|----------|
| S01 | Login | All | P0 |
| S02 | Dashboard | All | P0 |
| S03 | Submit Expense | Submitter | P0 |
| S04 | Expense List | All | P0 |
| S05 | Expense Detail | All | P0 |
| S06 | Approval Action | Manager | P0 |
| S07 | Policy List | Admin/Finance | P1 |
| S08 | Policy Editor | Admin/Finance | P1 |
| S09 | Audit Log | Admin/Finance | P1 |
| S10 | User Settings | All | P2 |

---

## Wireframe Descriptions

### S01: Login Screen

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                         Expense Policy Enforcer                  │
│                                                                 │
│    ┌─────────────────────────────────────────────────────┐     │
│    │                                                      │     │
│    │           📋                                         │     │
│    │                                                      │     │
│    │         Welcome Back                                 │     │
│    │                                                      │     │
│    │    Email                                            │     │
│    │    ┌──────────────────────────────────────────┐    │     │
│    │    │ sarah@company.com                         │    │     │
│    │    └──────────────────────────────────────────┘    │     │
│    │                                                      │     │
│    │    Password                                         │     │
│    │    ┌──────────────────────────────────────────┐    │     │
│    │    │ ••••••••••••••••••             [👁]      │    │     │
│    │    └──────────────────────────────────────────┘    │     │
│    │                                                      │     │
│    │    ☐ Remember me    Forgot password?                │     │
│    │                                                      │     │
│    │    ┌──────────────────────────────────────────┐    │     │
│    │    │           Sign In                         │    │     │
│    │    └──────────────────────────────────────────┘    │     │
│    │                                                      │     │
│    │    ─────────────── or ───────────────               │     │
│    │                                                      │     │
│    │    ┌──────────────────────────────────────────┐    │     │
│    │    │   G  Sign in with Google                 │    │     │
│    │    └──────────────────────────────────────────┘    │     │
│    │                                                      │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Clean, centered card layout
- Email + password fields
- "Remember me" checkbox
- Forgot password link
- SSO option (Google)
- Link to register (if self-signup enabled)

---

### S02: Dashboard (Submitter View)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Expense Policy Enforcer        [🔔 2]  [👤 Sarah ▼]                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Dashboard                                      [+ New Expense] │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Pending     │  │  Approved    │  │  Rejected    │  │  Total     │  │
│  │     3        │  │     12       │  │     1        │  │  $2,450    │  │
│  │  expenses    │  │  this month  │  │  needs action│  │  this month│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Quick Actions                                                  │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │    │
│  │  │  📤 Submit  │  │  📋 My      │  │  📊 Reports │             │    │
│  │  │  Expense    │  │  Expenses   │  │             │             │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Recent Expenses                                        [View All]│   │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  Date       Vendor              Amount    Status                │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  Feb 19     Amazon AWS          $149.99   ⚠️ Pending Approval   │    │
│  │  Feb 18     Uber                $24.50    ✓ Approved            │    │
│  │  Feb 17     Starbucks           $8.75     ✓ Approved            │    │
│  │  Feb 15     Delta Airlines      $450.00   ⚠️ Pending Approval   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Policy Reminders                                               │    │
│  │  ⚠️ Expenses over $100 require manager approval                 │    │
│  │  📎 Receipts required for expenses over $25                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Top navigation with notifications and user menu
- Stats cards (Pending, Approved, Rejected, Total)
- Quick action buttons
- Recent expenses table
- Policy reminders

---

### S03: Submit Expense

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard         Submit Expense                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Step 1 of 3: Upload Receipt                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                           │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                                                                  │    │
│  │         ┌─────────────────────────────────────────┐             │    │
│  │         │                                          │             │    │
│  │         │           📎 Drop receipt here          │             │    │
│  │         │           or click to browse            │             │    │
│  │         │                                          │             │    │
│  │         │   Supported: JPG, PNG, PDF (max 10MB)   │             │    │
│  │         │                                          │             │    │
│  │         └─────────────────────────────────────────┘             │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Or enter manually                                              │    │
│  │                                                                  │    │
│  │  Vendor *          Amount *          Date *          Category * │    │
│  │  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌─────────┐│    │
│  │  │           │    │ $         │    │ MM/DD/YYYY│    │ Select ▼││    │
│  │  └───────────┘    └───────────┘    └───────────┘    └─────────┘│    │
│  │                                                                  │    │
│  │  Notes                                                           │    │
│  │  ┌───────────────────────────────────────────────────────────┐  │    │
│  │  │                                                           │  │    │
│  │  └───────────────────────────────────────────────────────────┘  │    │
│  │                                                                  │    │
│  │                                    [Cancel]  [Continue →]       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Progress indicator (Step 1 of 3)
- Drag-and-drop upload zone
- Manual entry fallback
- Form validation (required fields marked with *)
- Category dropdown

---

### S04: Review OCR Data

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ← Back                    Submit Expense                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Step 2 of 3: Review Extracted Data                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                           │
│                                                                          │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │                             │  │  Receipt Preview                │   │
│  │     RECEIPT IMAGE           │  │  ┌─────────────────────────┐   │   │
│  │     (Uploaded)              │  │  │ AMAZON WEB SERVICES     │   │   │
│  │                             │  │  │                         │   │   │
│  │                             │  │  │ Amount: $149.99        │   │   │
│  │                             │  │  │ Date: Feb 19, 2026     │   │   │
│  │                             │  │  └─────────────────────────┘   │   │
│  │                             │  │                                │   │
│  │                             │  │  [Replace Image]               │   │
│  └─────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Extracted Information                              [Edit]      │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │                                                                  │    │
│  │  Vendor          Amazon Web Services              ✓ Confirmed   │    │
│  │  Amount          $149.99                          ✓ Confirmed   │    │
│  │  Date            February 19, 2026                ✓ Confirmed   │    │
│  │  Category        Software & Services              [Change]      │    │
│  │  Tax             $12.00                           ✓ Confirmed   │    │
│  │                                                                  │    │
│  │  OCR Confidence: 96%  ✓ High                                     │    │
│  │                                                                  │    │
│  │  ⚠️ Policy Check: This expense requires manager approval        │    │
│  │     Reason: Amount ($149.99) exceeds threshold ($100.00)        │    │
│  │                                                                  │    │
│  │                                    [← Back]  [Submit Expense]   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Side-by-side receipt preview + extracted data
- Confidence indicators for each field
- Edit capability for corrections
- Policy violation warning (real-time)
- Clear submit action

---

### S05: Success Confirmation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                                                                          │
│                          ✓                                               │
│                     Success!                                             │
│                                                                          │
│              Your expense has been submitted                             │
│                                                                          │
│         ┌─────────────────────────────────────────────────────┐         │
│         │                                                      │         │
│         │   Vendor:    Amazon Web Services                     │         │
│         │   Amount:    $149.99                                 │         │
│         │   Status:    ⚠️ Pending Manager Approval             │         │
│         │                                                      │         │
│         │   Mike (your manager) has been notified              │         │
│         │   Expected approval time: 24-48 hours                │         │
│         │                                                      │         │
│         └─────────────────────────────────────────────────────┘         │
│                                                                          │
│              ┌──────────────┐     ┌──────────────┐                      │
│              │ View Details │     │ Submit Another│                     │
│              └──────────────┘     └──────────────┘                      │
│                                                                          │
│                                                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Large success checkmark
- Summary of submitted expense
- Clear status indicator
- Next steps explained
- Two action options

---

### S06: Expense List (Manager View)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Expense Policy Enforcer        [🔔 5]  [👤 Mike ▼]                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Pending Approvals                               Filter: [All ▼]│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ⚠️ 5 expenses awaiting your approval                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ☐  Employee     Vendor           Amount    Date     Status    │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  ☐  Sarah Chen   Amazon AWS       $149.99   Feb 19   ⚠️ Review │    │
│  │  ☐  John Doe     Delta Airlines   $450.00   Feb 18   ⚠️ Review │    │
│  │  ☐  Sarah Chen   Client Lunch     $85.00    Feb 17   ⚠️ Review │    │
│  │  ☐  Emma Wilson  Office Depot     $32.50    Feb 16   ✓ Auto    │    │
│  │  ☐  John Doe     Uber             $18.75    Feb 15   ✓ Auto    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  [Select All]  [Approve Selected (3)]  [Reject Selected]                │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Recently Approved                                              │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  Sarah Chen   Starbucks        $8.75     Feb 14   ✓ Approved   │    │
│  │  Emma Wilson  Best Buy         $199.99   Feb 13   ✓ Approved   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Clear "Pending Approvals" header with count
- Checkbox selection for bulk actions
- Status badges (⚠️ Review, ✓ Auto)
- Bulk approve/reject actions
- Recently approved section

---

### S07: Expense Detail (Approval View)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ← Back to Pending                              Expense #EXP-2026-0042  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ⚠️ Requires Manager Approval                                   │    │
│  │  Policy: Expenses over $100 require approval                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │  Expense Details            │  │  Receipt                        │   │
│  │  ─────────────────────────  │  │  ┌─────────────────────────┐   │   │
│  │                             │  │  │                         │   │   │
│  │  Employee:  Sarah Chen      │  │  │   RECEIPT IMAGE         │   │   │
│  │  Department: Engineering    │  │  │                         │   │   │
│  │                             │  │  │                         │   │   │
│  │  Vendor:    Amazon AWS      │  │  │                         │   │   │
│  │  Amount:    $149.99         │  │  │                         │   │   │
│  │  Date:      Feb 19, 2026    │  │  │                         │   │   │
│  │  Category:  Software        │  │  │                         │   │   │
│  │                             │  │  │                         │   │   │
│  │  Notes:                     │  │  │                         │   │   │
│  │  Monthly cloud              │  │  │                         │   │   │
│  │  infrastructure             │  │  │                         │   │   │
│  │                             │  │  └─────────────────────────┘   │   │
│  │  Submitted: Feb 19, 2026    │  │                                │   │
│  │  10:30 AM                   │  │  [Download] [Enlarge]          │   │
│  └─────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Policy Violations                                              │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  ⚠️ Amount ($149.99) exceeds manager approval threshold ($100) │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Decision                                                       │    │
│  │                                                                 │    │
│  │  Comments (optional):                                           │    │
│  │  ┌───────────────────────────────────────────────────────────┐ │    │
│  │  │ Approved - within Q1 infrastructure budget                │ │    │
│  │  └───────────────────────────────────────────────────────────┘ │    │
│  │                                                                 │    │
│  │                        [🚫 Reject]     [✓ Approve Expense]     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Policy violation banner at top
- Two-column layout (details + receipt)
- Employee context (department, history)
- Optional comment field
- Clear approve/reject buttons (color-coded)

---

### S08: Policy List (Admin View)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Expense Policy Enforcer        [🔔 0]  [👤 Lisa ▼]                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Policy Management                              [+ New Policy]  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Active Policies (5)                                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  🟢  Manager Approval for Expenses >$100                       │    │
│  │      If amount > $100 → Require manager approval               │    │
│  │      Last updated: Feb 1, 2026 by Lisa                         │    │
│  │                                    [Edit] [Duplicate] [Disable] │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  🟢  Receipt Required for Expenses >$25                        │    │
│  │      If amount > $25 → Require receipt upload                  │    │
│  │      Last updated: Feb 1, 2026 by Lisa                         │    │
│  │                                    [Edit] [Duplicate] [Disable] │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  🟢  Auto-reject Gambling                                      │    │
│  │      If category = Gambling → Auto-reject                      │    │
│  │      Last updated: Feb 1, 2026 by Lisa                         │    │
│  │                                    [Edit] [Duplicate] [Disable] │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  🟢  Meals Per Diem $50                                        │    │
│  │      If category = Meals AND amount > $50 → Require approval   │    │
│  │      Last updated: Feb 1, 2026 by Lisa                         │    │
│  │                                    [Edit] [Duplicate] [Disable] │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  🟢  Auto-approve Office Supplies <$25                         │    │
│  │      If category = Office Supplies AND amount < $25 → Approve  │    │
│  │      Last updated: Feb 1, 2026 by Lisa                         │    │
│  │                                    [Edit] [Duplicate] [Disable] │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Inactive Policies (2)                              [Show]      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Status indicators (🟢 Active, ⚪ Inactive)
- Rule summary in plain English
- Last updated metadata
- Action buttons (Edit, Duplicate, Disable)
- Collapsed inactive policies

---

### S09: Policy Editor

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ← Back to Policies              Edit Policy                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Basic Information                                              │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  Policy Name *                                                  │    │
│  │  ┌───────────────────────────────────────────────────────────┐ │    │
│  │  │ Manager Approval for Expenses >$100                      │ │    │
│  │  └───────────────────────────────────────────────────────────┘ │    │
│  │                                                                 │    │
│  │  Description                                                    │    │
│  │  ┌───────────────────────────────────────────────────────────┐ │    │
│  │  │ Any expense above $100 requires prior approval from a    │ │    │
│  │  │ manager before processing.                                │ │    │
│  │  └───────────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Rule Condition                                                 │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │                                                                 │    │
│  │  If  [Amount ▼]  [greater than ▼]  [$ ──────]                  │    │
│  │                                           100                  │    │
│  │                                                                 │    │
│  │  + Add Another Condition (AND/OR)                              │    │
│  │                                                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Then                                                           │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │                                                                 │    │
│  │  [Require Manager Approval ▼]                                   │    │
│  │                                                                 │    │
│  │  Approver: [Manager Role ▼]                                     │    │
│  │                                                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Preview                                                        │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  "If expense amount is greater than $100, require manager      │    │
│  │   approval from the employee's direct manager."                │    │
│  │                                                                 │    │
│  │  [Test with Sample Data]                                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│                          [Cancel]  [Save Policy]                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Natural language rule builder
- Dropdown selectors for conditions
- Visual AND/OR logic
- Plain English preview
- Test button for validation

---

### S10: Audit Log

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ← Back                    Audit Log                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Audit Trail                                    [📥 Export CSV] │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Filters:                                                               │
│  [Date Range ▼]  [User ▼]  [Action Type ▼]  [Expense ID ▼]  [Apply]    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Timestamp          User          Action        Expense    Details│   │
│  │  ──────────────────────────────────────────────────────────────  │    │
│  │  Feb 19 11:45     Mike Chen    Approved     EXP-042   ✓ Within  │    │
│  │  2026 AM                        (expense)              budget    │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  Feb 19 10:30     Sarah Chen   Submitted    EXP-042   Amazon   │    │
│  │  2026 AM                        (expense)              AWS      │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  Feb 19 10:30     System       Flagged      EXP-042   Policy  │    │
│  │  2026 AM                        (violation)            >$100   │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  Feb 19 09:15     Lisa Park    Created      POL-006   Meals   │    │
│  │  2026 AM                        (policy)             $50 limit │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  Feb 18 16:20     John Doe     Rejected     EXP-041   ❌ No    │    │
│  │  2026 PM                        (expense)              receipt  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Showing 1-5 of 247 entries     [← Previous]  [1] [2] [3]  [Next →]    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Filter controls (date, user, action type)
- Chronological entries
- Action icons (✓, ❌, ⚠️)
- Export functionality
- Pagination

---

## Design Style Guide

### Color Palette

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COLOR PALETTE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PRIMARY                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │          │  │          │  │          │  │          │  │          │  │
│  │ #2563EB  │  │ #1D4ED8  │  │ #1E40AF  │  │ #DBEAFE  │  │ #EFF6FF  │  │
│  │ Blue 600 │  │ Blue 700 │  │ Blue 800 │  │ Blue 100 │  │ Blue 50  │  │
│  │ Primary  │  │ Hover    │  │ Active   │  │ Background│  │ Subtle  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                                          │
│  STATUS                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │          │  │          │  │          │  │          │  │          │  │
│  │ #10B981  │  │ #EF4444  │  │ #F59E0B  │  │ #6B7280  │  │ #8B5CF6  │  │
│  │ Green 500│  │ Red 500  │  │ Amber 500│  │ Gray 500 │  │ Purple 500│ │
│  │ Success  │  │ Error    │  │ Warning  │  │ Neutral  │  │ Info     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                                          │
│  NEUTRALS                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │          │  │          │  │          │  │          │  │          │  │
│  │ #111827  │  │ #374151  │  │ #6B7280  │  │ #F3F4F6  │  │ #FFFFFF  │  │
│  │ Gray 900 │  │ Gray 700 │  │ Gray 500 │  │ Gray 100 │  │ White    │  │
│  │ Text     │  │ Secondary│  │ Muted    │  │ Border   │  │ Background│ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Typography

```
FONT FAMILY
───────────
Primary: Inter (Google Fonts)
Fallback: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif

FONT SIZES
──────────
xs:   12px (0.75rem)   - Captions, labels
sm:   14px (0.875rem)  - Secondary text, buttons
base: 16px (1rem)      - Body text, inputs
lg:   18px (1.125rem)  - Subheadings
xl:   20px (1.25rem)   - Section titles
2xl:  24px (1.5rem)    - Page titles
3xl:  30px (1.875rem)  - Hero text

FONT WEIGHTS
────────────
Regular: 400 - Body text
Medium:  500 - Buttons, labels
Semibold: 600 - Headings, emphasis
Bold:    700 - Primary actions, stats
```

### Spacing System

```
BASE UNIT: 4px

SCALE
─────
1:  4px    (0.25rem)  - Tight spacing
2:  8px    (0.5rem)   - Component padding
3:  12px   (0.75rem)  - Element spacing
4:  16px   (1rem)     - Standard gap
5:  20px   (1.25rem)  - Section padding
6:  24px   (1.5rem)   - Large gaps
8:  32px   (2rem)     - Section margins
10: 40px   (2.5rem)   - Page margins
12: 48px   (3rem)     - Hero spacing
```

### Component Styles

#### Buttons

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BUTTON STYLES                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PRIMARY BUTTON                                                         │
│  ┌─────────────────────────────────────────┐                           │
│  │         Submit Expense                  │  h: 40px                  │
│  │         (White text, Blue #2563EB bg)   │  px: 24px                 │
│  └─────────────────────────────────────────┘  radius: 8px              │
│                                                  shadow: sm             │
│  HOVER STATE                                                          │
│  ┌─────────────────────────────────────────┐                           │
│  │         Submit Expense                  │  bg: #1D4ED8              │
│  └─────────────────────────────────────────┘  shadow: md               │
│                                                                          │
│  SECONDARY BUTTON                                                       │
│  ┌─────────────────────────────────────────┐                           │
│  │         Cancel                          │  h: 40px                  │
│  │         (Blue text, White bg)           │  px: 24px                 │
│  └─────────────────────────────────────────┘  radius: 8px              │
│                                                  border: 1px #2563EB    │
│  DANGER BUTTON                                                          │
│  ┌─────────────────────────────────────────┐                           │
│  │         Reject Expense                  │  h: 40px                  │
│  │         (White text, Red #EF4444 bg)    │  px: 24px                 │
│  └─────────────────────────────────────────┘  radius: 8px              │
│                                                                          │
│  DISABLED STATE                                                         │
│  ┌─────────────────────────────────────────┐                           │
│  │         Submit                          │  bg: #E5E7EB              │
│  │         (Gray text, cursor: not-allowed)│  color: #9CA3AF           │
│  └─────────────────────────────────────────┘                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Status Badges

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        STATUS BADGES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PENDING                                                                │
│  ┌─────────────────────────┐                                           │
│  │  ⚠️  Pending            │  bg: #FEF3C7 (Amber 100)                 │
│  └─────────────────────────┘  text: #92400E (Amber 800)               │
│                                 px: 12px, py: 4px, radius: 9999px     │
│                                                                          │
│  APPROVED                                                               │
│  ┌─────────────────────────┐                                           │
│  │  ✓  Approved            │  bg: #D1FAE5 (Green 100)                 │
│  └─────────────────────────┘  text: #065F46 (Green 800)               │
│                                                                          │
│  REJECTED                                                               │
│  ┌─────────────────────────┐                                           │
│  │  ✕  Rejected            │  bg: #FEE2E2 (Red 100)                   │
│  └─────────────────────────┘  text: #991B1B (Red 800)                 │
│                                                                          │
│  NEEDS REVIEW                                                           │
│  ┌─────────────────────────┐                                           │
│  │  🔍  Needs Review       │  bg: #E0E7FF (Purple 100)                │
│  └─────────────────────────┘  text: #3730A3 (Purple 800)              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Input Fields

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INPUT FIELD STYLES                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DEFAULT STATE                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Vendor                                                          │   │
│  │  ┌───────────────────────────────────────────────────────────┐ │   │
│  │  │                                                           │ │   │
│  │  └───────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  h: 40px, border: 1px #D1D5DB, radius: 8px                            │
│  focus: border #2563EB, ring: 2px #DBEAFE                             │
│                                                                          │
│  ERROR STATE                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Amount *                                                        │   │
│  │  ┌───────────────────────────────────────────────────────────┐ │   │
│  │  │ Invalid amount                              ⚠️            │ │   │
│  │  └───────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  border: 1px #EF4444, error text: #DC2626                              │
│                                                                          │
│  DISABLED STATE                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ID (Auto-generated)                                             │   │
│  │  ┌───────────────────────────────────────────────────────────┐ │   │
│  │  │ EXP-2026-0042                              (gray bg)      │ │   │
│  │  └───────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  bg: #F3F4F6, color: #6B7280, cursor: not-allowed                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Accessibility Considerations

### WCAG 2.1 AA Compliance

| Requirement | Implementation |
|-------------|----------------|
| **Color Contrast** | All text meets 4.5:1 ratio minimum |
| **Keyboard Navigation** | All interactive elements focusable via Tab |
| **Focus Indicators** | 2px blue ring on all focused elements |
| **Screen Reader Support** | ARIA labels on all buttons, icons, form fields |
| **Error Identification** | Clear error messages with field association |
| **Text Scaling** | Supports up to 200% zoom without breaking |
| **Motion Reduction** | Respects `prefers-reduced-motion` |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + N` | New Expense |
| `Ctrl/Cmd + Enter` | Submit form |
| `Escape` | Close modal/cancel |
| `Ctrl/Cmd + K` | Quick search |
| `?` | Show keyboard shortcuts |

### Screen Reader Announcements

```html
<!-- Live regions for dynamic updates -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
  Expense submitted successfully. Pending manager approval.
</div>

<!-- Skip links -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

### Icon + Text Pattern

```
✅ CORRECT: Icon with text label
┌─────────────────┐
│  📤 Submit      │
└─────────────────┘

❌ WRONG: Icon only (unclear meaning)
┌─────┐
│  📤 │
└─────┘
```

---

## Responsive Breakpoints

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      RESPONSIVE BREAKPOINTS                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  MOBILE (< 640px)                                                       │
│  ─────────────────                                                      │
│  • Single column layout                                                 │
│  • Full-width buttons                                                   │
│  • Hamburger menu navigation                                            │
│  • Stacked form fields                                                  │
│  • Touch-friendly tap targets (44px minimum)                            │
│                                                                          │
│  TABLET (640px - 1024px)                                                │
│  ─────────────────────                                                  │
│  • Two column layouts where appropriate                                 │
│  • Side-by-side receipt + form on submit                                │
│  • Visible navigation bar                                               │
│  • Table becomes card-based or horizontally scrollable                  │
│                                                                          │
│  DESKTOP (> 1024px)                                                     │
│  ─────────────────                                                      │
│  • Full multi-column layouts                                            │
│  • Sidebars visible                                                     │
│  • Hover states on all interactive elements                             │
│  • Keyboard shortcuts available                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*UI/UX Design Document v1.0 • Expense Policy Enforcer • Hackathon Zero*

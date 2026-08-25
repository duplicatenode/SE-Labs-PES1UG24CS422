## Lab 1: Requirements Engineering & UML Use-Case Modelling

**Problem Statement #53 | Media, Events & Community**
**Title:** Freelance Content Creator Escrow Platform

---

## 1. Problem Context

A freelance contract management system that allows content creators and client sponsors to
define deliverable milestones, review watermarked draft assets, and trigger secure milestone
payment releases from escrow.

**Stakeholders / Actors:** Content Creator, Client Sponsor *(Payment Gateway as external supporting actor)*

---

## 2. Repository Contents

```
Lab1/
├── Requirements_Table.docx   # 5 Functional + 2 Non-Functional Requirements
├── usecase_diagram.pdf       # UML Use-Case Diagram (actors, use cases, <<include>>/<<extend>>)
└── UseCase_Flow.docx         # 1-page flow spec: Release Milestone Payment
```

| File | Description |
|---|---|
| `Requirements_Table.docx` | FR-001–FR-005 and NFR-001–NFR-002, each with Req ID, Type, Description, Priority, Acceptance Criteria, and Rationale. |
| `usecase_diagram.pdf` | UML Use-Case Diagram showing all actors and 10 use cases, including at least one `<<include>>` (Submit Draft Deliverable → Apply Watermark; Release Milestone Payment → Process Payment) and one `<<extend>>` (Request Revision → Review Draft) relationship. |
| `UseCase_Flow.docx` | Use-case flow specification for **UC-08: Release Milestone Payment**, detailing Preconditions, Postconditions, Main Success Scenario, and an Alternate Flow (payment declined). |

---

## 3. Actors & Core Use Cases

- **Content Creator** — submits draft deliverables, receives milestone payments.
- **Client Sponsor** — reviews drafts, approves/rejects milestones, releases payment.
- **Payment Gateway** *(external)* — processes and authorizes fund transfers.

Core use cases: Register/Login, Create Contract & Define Milestones, Submit Draft Deliverable,
Apply Watermark, Review Draft, Request Revision, Approve Milestone, Release Milestone Payment,
Process Payment, Receive Notification.

---

## 4. Tools Used

- UML diagram: matplotlib-based diagram export (draw.io-equivalent layout)
- Documents: Word (.docx)

---

## Author

*SARTHKI VACHHANI*
*PES1UG24CS422*
*5 G*

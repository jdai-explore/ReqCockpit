# Product Requirements Document (PRD)
## The Local Cockpit: Multi-Partner Requirements Aggregation Tool

| Attribute | Value |
|:---|:---|
| **Product Name** | **The Local Cockpit** (Internal Codename: Project REX - Requirements Exchange) |
| **Version** | 1.0 (MVP) |
| **Document Version** | 2.0 - Enhanced |
| **Product Owner** | Requirements Manager |
| **Target Release** | Q2 2026 |
| **Status** | Ready for Development |
| **Last Updated** | December 2025 |

---

## 1. Executive Summary

### 1.1 Vision Statement
The Local Cockpit revolutionizes the Stakeholder Request Clarification (SRC) process in automotive supply chains by providing a **privacy-first, high-performance desktop application** that enables Customer Requirements Engineers (CustREs) to aggregate, compare, and resolve supplier feedback across multiple iterations with unprecedented speed and transparency.

### 1.2 Problem Statement
In multi-tier automotive development, CustREs face three critical challenges:

**Challenge 1: Manual Reconciliation Hell**
- Hours spent comparing 10+ ReqIF files from different suppliers
- Copy-paste errors lead to specification misalignment
- No single view of requirement status across supply base

**Challenge 2: Data Sensitivity Barriers**
- Cloud solutions violate IP protection policies
- Advanced feature specifications too sensitive for external hosting
- Legal and compliance risks with third-party platforms

**Challenge 3: Audit Trail Gaps**
- Difficult to track *when* requirements changed
- Cannot prove *which iteration* feedback came from
- No clear history of clarification decisions

### 1.3 Solution Overview
The Local Cockpit provides:

1. **Automated Multi-Supplier Aggregation**: Import ReqIF files from all suppliers, automatically align by ReqIF ID, display side-by-side in unified grid
2. **Privacy-First Architecture**: 100% local processing with SQLite storage - data never leaves the machine
3. **Iteration-Based Audit Trail**: Tag each import with Iteration ID, maintain complete time-series history
4. **Conflict Detection Engine**: Automatically flag requirements where suppliers disagree
5. **Fast Performance**: Sub-5-second load times for 500+ requirements with 10 supplier responses

---

## 2. Goals & Success Metrics

### 2.1 Primary Objectives

| Objective | Target Metric | Measurement Method |
|:---|:---|:---|
| **Speed SRC Cycle** | 50% reduction in cycle time for 500-req spec | Time tracking from import to final decision |
| **Eliminate Data Errors** | Zero data corruption/mismatch errors | Validation reports on 100 production exchanges |
| **Performance Excellence** | Full aggregation in <5 seconds | Automated performance tests |
| **User Adoption** | 80% of CustREs use as primary tool within 1 month | Usage analytics |
| **Conflict Resolution** | 90% of conflicts resolved in first iteration | Tracking dashboard metrics |

### 2.2 Key Performance Indicators (KPIs)

**Operational KPIs:**
- Average time per requirement decision: < 2 minutes
- Number of supplier roundtrips required: < 3 iterations
- User satisfaction score: > 4.5/5.0

**Technical KPIs:**
- Parser success rate: > 99.5%
- UI responsiveness: < 100ms for grid interactions
- Database query time: < 50ms for 1000 requirements

---

## 3. User Personas & Use Cases

### 3.1 Primary Persona: Customer Requirements Engineer (CustRE)

**Profile:**
- Manages 5-15 supplier relationships simultaneously
- Handles 300-800 requirements per project
- Works in 2-4 week clarification cycles
- Needs audit trail for ISO 26262 compliance

**Key Activities:**
1. Import Master Specification (OEM's golden source)
2. Import supplier responses across multiple iterations
3. Compare supplier statuses side-by-side
4. Identify conflicts and clarification needs
5. Document final decisions with rationale
6. Export consolidated results for stakeholders

**Pain Points:**
- Switching between 10+ DOORS modules
- Manual Excel reconciliation
- Lost track of iteration history
- Unable to prove compliance decisions

**Success Criteria:**
- Can process 10 supplier files in < 15 minutes
- Clear visibility of all conflicts
- Complete audit trail for regulatory review

### 3.2 Secondary Persona: Systems Engineer

**Profile:**
- Reviews consolidated feedback for feasibility
- Needs to understand cross-supplier patterns
- Identifies system-level impacts

**Key Activities:**
1. Review dashboard for overall acceptance rates
2. Analyze clusters of rejected requirements
3. Identify technical showstoppers early

### 3.3 Tertiary Persona: Project Manager

**Profile:**
- Needs executive overview of SRC health
- Tracks progress toward milestones
- Reports to steering committees

**Key Activities:**
1. View dashboard metrics
2. Generate status reports
3. Monitor critical blockers

---

## 4. Functional Requirements

### 4.1 Project & Data Management

**REQ-001: Project Creation**
- **Priority**: P0 (Blocker)
- **Description**: User shall create new local project with unique name
- **Acceptance Criteria**:
  - Creates `[ProjectName].sqlite` file in user-selected directory
  - Initializes database schema
  - Shows confirmation message
  - Project appears in recent projects list

**REQ-002: Master Specification Import**
- **Priority**: P0
- **Description**: User shall import Master Specification as source of truth
- **Acceptance Criteria**:
  - Accepts .reqif and .reqifz files
  - Validates file structure using custom parser
  - Extracts all SPEC-OBJECTs with attributes
  - Stores in `master_requirements` table
  - Shows import summary (count, warnings, errors)
  - Completes import in < 10 seconds for 500 requirements

**REQ-003: Iteration Management**
- **Priority**: P0
- **Description**: Each supplier import must be tagged with unique, immutable Iteration ID
- **Acceptance Criteria**:
  - Modal dialog forces user to define Iteration ID before import
  - Format: `I-XXX_Description` (e.g., "I-003_Final_Quotes")
  - System validates uniqueness within project
  - Iteration ID stored with every supplier response record
  - User can view/select iterations from dropdown
  - System prevents modification of past Iteration IDs

**REQ-004: Supplier Response Import**
- **Priority**: P0
- **Description**: User shall import supplier ReqIF responses and link to master requirements
- **Acceptance Criteria**:
  - Accepts multiple files in single import session
  - Matches supplier requirements to master by ReqIF ID (IDENTIFIER field)
  - Handles missing/new requirements gracefully
  - Extracts ReqIF-WF.SupplierStatus and ReqIF-WF.SupplierComment
  - Stores in `supplier_feedback` table with iteration_id and supplier_name
  - Shows matching summary (matched, unmatched, new)
  - Completes in < 5 seconds for 500 requirements per supplier

### 4.2 Requirements Cockpit View

**REQ-005: Side-by-Side Comparison Grid**
- **Priority**: P0
- **Description**: Main view displays master requirement alongside all supplier responses
- **Acceptance Criteria**:
  - Columns: [ReqIF ID | Master Text | Supplier1 Status | Supplier1 Comment | Supplier2 Status | ... ]
  - One row per master requirement
  - Shows data for currently selected Iteration ID
  - Supports up to 20 suppliers per view
  - Pagination for > 100 requirements
  - Grid renders in < 2 seconds

**REQ-006: Frozen Context Columns**
- **Priority**: P0
- **Description**: ReqIF ID and Master Text columns must remain visible during horizontal scroll
- **Acceptance Criteria**:
  - First 2 columns (ReqIF ID, Master Text) are frozen
  - Supplier columns scroll horizontally
  - Frozen columns have visual separator
  - Scrolling is smooth (60fps)

**REQ-007: Status Harmonization**
- **Priority**: P0
- **Description**: System normalizes supplier-specific status values to standard set
- **Acceptance Criteria**:
  - Maps common variants: "OK"/"Compliant"/"Accepted" → **Accepted (Green)**
  - Maps: "Needs Clarification"/"ToBeClarified" → **Clarification Needed (Yellow)**
  - Maps: "Not Accepted"/"NotAgreed"/"Rejected" → **Rejected (Red)**
  - Mapping rules configurable per supplier
  - Unknown statuses show as warning icon with original text
  - Status shown as colored badge in grid

**REQ-008: Conflict Detection & Highlighting**
- **Priority**: P0
- **Description**: System automatically flags rows with supplier disagreements
- **Acceptance Criteria**:
  - Conflict = 2+ suppliers with different negative statuses (Yellow/Red combinations)
  - Conflict rows highlighted with amber/orange background
  - Conflict icon in leftmost column
  - Conflict count shown in dashboard
  - User can filter to show only conflicts
  - Conflict detection runs in < 500ms

**REQ-009: Text Filtering & Search**
- **Priority**: P1
- **Description**: User can filter requirements by text, status, or supplier
- **Acceptance Criteria**:
  - Global text search across ReqIF ID and Master Text
  - Filter by status: Accepted/Clarification/Rejected/Conflict
  - Filter by supplier (show/hide columns)
  - Multiple filters apply as AND logic
  - Search updates in < 200ms
  - Clear all filters button

**REQ-010: Master Text Rendering**
- **Priority**: P1
- **Description**: Display master requirement text readably
- **Acceptance Criteria**:
  - MVP: Plain text extraction from XHTML
  - Sanitize HTML entities
  - Line breaks preserved
  - Max height with "Show More" for long text
  - No embedded objects in MVP

### 4.3 Dashboard & Analytics

**REQ-011: Status Overview Dashboard**
- **Priority**: P0
- **Description**: Dashboard shows aggregated KPIs for current iteration
- **Acceptance Criteria**:
  - Cards showing: Total Requirements, Accepted Count, Clarification Needed, Rejected, Conflicts Detected
  - Color-coded cards (green/yellow/red)
  - Percentages calculated automatically
  - Updates when iteration selected
  - Click card to filter grid to that status

**REQ-012: Supplier Comparison View**
- **Priority**: P1
- **Description**: Visualize acceptance rates per supplier
- **Acceptance Criteria**:
  - Horizontal bar chart: Supplier name | % Accepted | % Clarification | % Rejected
  - Sort by acceptance rate (descending)
  - Hover shows exact counts
  - Export to PNG
  - Updates with iteration selection

**REQ-013: Iteration Timeline View**
- **Priority**: P2
- **Description**: Show status evolution across iterations
- **Acceptance Criteria**:
  - Timeline view showing all iterations chronologically
  - For each iteration: date, acceptance %, clarification %, rejected %
  - Line chart showing trend
  - Click iteration to load in grid

### 4.4 Resolution & Decision Making

**REQ-014: CustRE Decision Logging**
- **Priority**: P0
- **Description**: User can record final decision for each requirement
- **Acceptance Criteria**:
  - Decision status: Accepted / Rejected / Modified / Deferred
  - Free-text "Action Note" field (max 2000 chars)
  - Decision and note stored in `custre_decisions` table
  - Linked to requirement_id, iteration_id, timestamp, user
  - Decision badge appears in grid
  - Unsaved decisions show warning before exit

**REQ-015: Bulk Decision Operations**
- **Priority**: P1
- **Description**: Apply decisions to multiple requirements at once
- **Acceptance Criteria**:
  - Select multiple rows (checkbox)
  - Bulk actions: Accept All, Reject All, Mark for Clarification
  - Confirmation dialog shows count
  - Bulk action logged as single audit entry
  - Completes in < 2 seconds for 100 requirements

**REQ-016: Decision History**
- **Priority**: P1
- **Description**: View complete history of decisions for a requirement
- **Acceptance Criteria**:
  - Click requirement → show history modal
  - Displays: Iteration | Date | User | Decision | Note
  - Sortable by date
  - Export history to CSV

### 4.5 Export & Reporting

**REQ-017: Consolidated Export**
- **Priority**: P0
- **Description**: Export aggregated data to CSV/XLSX
- **Acceptance Criteria**:
  - Format: ReqIF ID | Master Text | Supplier1 Status | ... | CustRE Decision | Action Note
  - Includes all visible suppliers for current iteration
  - Applies current filters
  - Excel has frozen header row and auto-sized columns
  - File saved to user-selected location
  - Export completes in < 5 seconds for 500 requirements

**REQ-018: Report Generation**
- **Priority**: P2
- **Description**: Generate formatted PDF report
- **Acceptance Criteria**:
  - Cover page with project name, iteration, date
  - Executive summary with dashboard metrics
  - Supplier comparison chart
  - Conflict list with details
  - PDF generated in < 10 seconds
  - Professional styling

---

## 5. Technical Architecture

### 5.1 Architecture Overview

**Design Pattern**: Two-Tier Desktop Native Application

```
┌─────────────────────────────────────────────────────┐
│            Presentation Layer (Frontend)             │
│                                                      │
│  Tauri Shell + React UI + AG Grid / TanStack Table │
│                                                      │
│  - Project management screens                       │
│  - Requirements Cockpit (comparison grid)           │
│  - Dashboard & analytics views                      │
│  - Import/export wizards                            │
└─────────────────────────────────────────────────────┘
                         ↕ IPC
┌─────────────────────────────────────────────────────┐
│          Data Engine Layer (Backend)                │
│                                                      │
│  Python + SQLAlchemy + Custom ReqIF Parser          │
│                                                      │
│  - ReqIF file parsing (custom parser reuse)         │
│  - SQLite database operations                       │
│  - Status harmonization logic                       │
│  - Conflict detection engine                        │
│  - Export generation                                │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│              Data Persistence Layer                  │
│                                                      │
│  SQLite Database ([ProjectName].sqlite)             │
│                                                      │
│  - master_requirements table                        │
│  - supplier_feedback table (with iteration_id)      │
│  - custre_decisions table                           │
│  - iterations table                                 │
│  - suppliers table                                  │
│  - status_mappings table                            │
└─────────────────────────────────────────────────────┘
```

### 5.2 Technology Stack

**Frontend:**
- **Framework**: Tauri 2.0 (Rust-based, minimal footprint)
- **UI Library**: React 18+ with TypeScript
- **Data Grid**: AG Grid Community (frozen columns, virtualization, performance) OR TanStack Table v8 (lighter, more control)
- **Styling**: Tailwind CSS 3.x
- **State Management**: Zustand or React Context
- **Charts**: Recharts (built-in with React integration)

**Backend:**
- **Language**: Python 3.11+
- **Parser**: Custom ReqIF parser (provided, enhanced)
- **Database**: SQLite 3.x (embedded, ACID compliant)
- **ORM**: SQLAlchemy 2.x
- **Data Processing**: Pandas (optional, for complex aggregations)

**Build & Distribution:**
- **Packaging**: Tauri bundler (creates native installers)
- **Platforms**: Windows 10/11, macOS 12+
- **Size Target**: < 50MB installer

### 5.3 Database Schema

**Core Tables:**

```sql
-- Projects metadata
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_opened TIMESTAMP,
    master_spec_filename TEXT,
    master_spec_imported_at TIMESTAMP
);

-- Iterations (time-series tagging)
CREATE TABLE iterations (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    iteration_id TEXT NOT NULL UNIQUE, -- e.g., "I-003_Final_Quotes"
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Suppliers
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT, -- for grid columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id, name),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Master Requirements (source of truth)
CREATE TABLE master_requirements (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    reqif_id TEXT NOT NULL, -- IDENTIFIER from ReqIF
    reqif_internal_id TEXT, -- internal ID if different
    requirement_type TEXT, -- from ReqIF-WF.Type
    text_content TEXT, -- extracted requirement text
    raw_attributes JSON, -- all ReqIF attributes as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id, reqif_id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Supplier Feedback (iteration-based)
CREATE TABLE supplier_feedback (
    id INTEGER PRIMARY KEY,
    master_req_id INTEGER NOT NULL,
    iteration_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    supplier_status TEXT, -- e.g., "Agreed", "ToBeClarified"
    supplier_status_normalized TEXT, -- harmonized: Accepted/Clarification/Rejected
    supplier_comment TEXT,
    raw_attributes JSON, -- all supplier attributes
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (master_req_id, iteration_id, supplier_id),
    FOREIGN KEY (master_req_id) REFERENCES master_requirements(id),
    FOREIGN KEY (iteration_id) REFERENCES iterations(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- CustRE Decisions
CREATE TABLE custre_decisions (
    id INTEGER PRIMARY KEY,
    master_req_id INTEGER NOT NULL,
    iteration_id INTEGER NOT NULL,
    decision_status TEXT NOT NULL, -- Accepted/Rejected/Modified/Deferred
    action_note TEXT,
    decided_by TEXT, -- username
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (master_req_id) REFERENCES master_requirements(id),
    FOREIGN KEY (iteration_id) REFERENCES iterations(id)
);

-- Status Mapping Rules (configurable)
CREATE TABLE status_mappings (
    id INTEGER PRIMARY KEY,
    supplier_id INTEGER,
    original_status TEXT NOT NULL,
    normalized_status TEXT NOT NULL, -- Accepted/Clarification/Rejected
    UNIQUE (supplier_id, original_status),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Indexes for performance
CREATE INDEX idx_master_reqif_id ON master_requirements(reqif_id);
CREATE INDEX idx_feedback_iteration ON supplier_feedback(iteration_id);
CREATE INDEX idx_feedback_master_req ON supplier_feedback(master_req_id);
CREATE INDEX idx_decisions_iteration ON custre_decisions(iteration_id);
```

### 5.4 ReqIF Parser Integration

**Custom Parser Enhancements:**

The provided `reqif_parser.py` is production-ready and will be used as-is with minor additions:

1. **Batch Import**: Process multiple files sequentially
2. **Progress Callbacks**: Report progress to UI during parsing
3. **Error Collection**: Collect all parsing errors without stopping
4. **Attribute Filtering**: Extract only SRC-relevant attributes (ReqIF-WF.SupplierStatus, ReqIF-WF.SupplierComment)

**Parser Reliability Strategy:**

From the PRD hints, we implement:
- **ReqIF ID Validation**: Check IDENTIFIER field first, fallback to LONG-NAME if GUID is unstable
- **Flexible Schema**: Use JSON column for unknown attributes
- **XHTML Handling**: Plain text extraction in MVP (as recommended)
- **Non-Standard Attributes**: Capture all, store in JSON, log warnings

### 5.5 Performance Optimizations

**Database:**
- Indexed queries on reqif_id, iteration_id
- Prepared statements for bulk inserts
- Transaction batching (commit every 100 records)
- VACUUM on project close

**Grid Rendering:**
- Virtual scrolling (render only visible rows)
- Lazy loading for large datasets
- Column virtualization for > 10 suppliers
- Debounced search/filter (300ms)

**Data Loading:**
- Load grid data in chunks (100 rows)
- Async queries don't block UI
- Cache dashboard metrics per iteration

---

## 6. Non-Functional Requirements

### 6.1 Performance

| Metric | Target | Measurement |
|:---|:---|:---|
| **Master Import** | < 10 sec for 500 reqs | Automated test |
| **Supplier Import** | < 5 sec per supplier (500 reqs) | Automated test |
| **Grid Load** | < 2 sec for 500 reqs × 10 suppliers | Automated test |
| **Search/Filter** | < 200ms response | UI profiler |
| **Decision Save** | < 100ms | Database profiler |
| **Export** | < 5 sec for 500 reqs | Automated test |

### 6.2 Privacy & Security

- **P-001**: All data processing occurs locally (no internet required)
- **P-002**: SQLite file stored in user-controlled directory
- **P-003**: No telemetry or analytics sent to external servers
- **P-004**: File permissions set to user-only access
- **P-005**: (Future) SQLite file encryption with user password

### 6.3 Reliability

- **R-001**: Single database connection per session (avoid locking)
- **R-002**: Automatic backup before each import (.sqlite.backup)
- **R-003**: Transaction rollback on import failure
- **R-004**: Graceful handling of corrupt ReqIF files (log error, continue)
- **R-005**: Crash recovery (detect incomplete transactions on startup)

### 6.4 Usability

- **U-001**: Onboarding wizard for first-time users (3 steps max)
- **U-002**: Context-sensitive help tooltips
- **U-003**: Keyboard shortcuts for common actions
- **U-004**: Undo/redo for bulk operations
- **U-005**: Responsive UI (no freezing during long operations)

### 6.5 Compatibility

- **C-001**: Windows 10 (64-bit), Windows 11
- **C-002**: macOS 12+ (Intel and Apple Silicon)
- **C-003**: ReqIF 1.0, 1.1, 1.2 (OMG standard)
- **C-004**: SQLite 3.35+

---

## 7. Out of Scope (Future Versions)

### V2.0 Features (Deferred)

**Enterprise Resilience:**
- Nexus/Artifactory integration for versioned SQLite backups
- AES-256 encryption for SQLite files
- Multi-user collaboration (shared database with row-level locking)

**Advanced ReqIF:**
- ReqIF roundtrip export (generate new ReqIF with CustRE decisions)
- Full XHTML rendering with embedded images
- OLE object support

**Workflow Automation:**
- Email notifications on import completion
- Scheduled reports
- Requirement approval workflow (multi-stage)

### V3.0 Features (Future)

**AI/Analytics:**
- Natural language search ("Show rejected requirements from Supplier A")
- Predictive conflict detection (based on historical patterns)
- Auto-suggest clarification text

**Integration:**
- DOORS export/import
- Polarion connector
- JIRA synchronization

---

## 8. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|:---|:---|:---|:---|
| **ReqIF Parser Fails on Vendor Dialects** | High | Medium | Extensive testing with real files; fallback to raw attribute storage |
| **SQLite Locking Issues** | High | Low | Single connection pattern; transaction batching; thorough testing |
| **Performance Degradation > 1000 Reqs** | Medium | Medium | Pagination; virtual scrolling; load testing with 2000+ reqs |
| **XHTML Rendering Complexity** | Low | High | Deferred to V2.0; plain text in MVP |
| **User Adoption Resistance** | Medium | Medium | Onboarding wizard; training sessions; clear value demonstration |

---

## 9. Success Criteria

### MVP Launch Criteria

**Must Have (P0):**
- ✅ Import master spec and 5 supplier responses
- ✅ Display side-by-side comparison grid with frozen columns
- ✅ Automatic status harmonization (3 standard statuses)
- ✅ Conflict detection and highlighting
- ✅ Iteration ID tagging
- ✅ CustRE decision logging
- ✅ Dashboard with KPIs
- ✅ Export to CSV/XLSX
- ✅ Load time < 5 seconds for 500 reqs × 10 suppliers
- ✅ Zero data corruption in 100 test imports

**Should Have (P1):**
- Text search and filtering
- Supplier comparison chart
- Bulk decision operations
- Decision history view

**Nice to Have (P2):**
- Iteration timeline
- PDF report generation
- Keyboard shortcuts

### Post-Launch Success (Month 1)

- 80% of target CustREs onboarded
- 50+ real projects created
- Average SRC cycle time reduced by 40%
- User satisfaction score > 4.0/5.0
- < 5 critical bugs reported

---

## 10. Development Approach

### 10.1 Agile Methodology

- **Sprint Duration**: 2 weeks
- **Team Size**: 2-3 developers (1 frontend, 1 backend, 0.5 QA)
- **Ceremonies**: Daily standup, sprint planning, demo, retrospective
- **Tools**: GitHub Projects, Discord/Slack

### 10.2 Release Strategy

**Phase 1: Core Infrastructure (Weeks 1-2)**
- Project setup, database schema, parser integration

**Phase 2: Data Import & Storage (Weeks 3-4)**
- Master import, supplier import, iteration management

**Phase 3: Cockpit View (Weeks 5-7)**
- Grid implementation, frozen columns, status display

**Phase 4: Dashboard & Analytics (Week 8)**
- KPI cards, supplier charts

**Phase 5: Decision & Export (Week 9)**
- Decision logging, CSV export

**Phase 6: Polish & Testing (Weeks 10-12)**
- Bug fixes, performance tuning, user testing

**Phase 7: Release (Week 12)**
- Installers, documentation, launch

---

# Work Breakdown Structure (WBS)

## Phase 1: Project Setup & Infrastructure (Week 1-2)

### 1.1 Development Environment Setup
**Duration**: 2 hours
- [ ] Install Tauri 2.0, Rust, Node.js
- [ ] Create project structure: `tauri init --app-name local-cockpit`
- [ ] Setup React + TypeScript + Vite
- [ ] Configure Tailwind CSS
- [ ] Initialize Git repository
- [ ] Create `.gitignore` and `README.md`
**Deliverable**: Running "Hello World" Tauri app

### 1.2 Python Backend Setup
**Duration**: 2 hours
- [ ] Setup Python 3.11+ virtual environment
- [ ] Install dependencies: SQLAlchemy, pandas (requirements.txt)
- [ ] Integrate provided `reqif_parser.py` into project
- [ ] Create `backend/` directory structure
- [ ] Setup Tauri IPC bridge for Python calls
- [ ] Test Python execution from Tauri
**Deliverable**: Tauri can call Python functions

### 1.3 Database Schema Implementation
**Duration**: 2 hours
- [ ] Create `backend/database/schema.py`
- [ ] Define SQLAlchemy models for all tables (projects, iterations, master_requirements, etc.)
- [ ] Implement database initialization function
- [ ] Create migration helper (simple version tracking)
- [ ] Write unit tests for schema creation
- [ ] Test database creation on Windows and macOS
**Deliverable**: `create_database()` function creates valid SQLite file

### 1.4 Project Manager Module
**Duration**: 2 hours
- [ ] Create `backend/project_manager.py`
- [ ] Implement `create_project(name, path)` function
- [ ] Implement `open_project(path)` function
- [ ] Implement `list_recent_projects()` function
- [ ] Add project metadata storage
- [ ] Write unit tests
**Deliverable**: Python module for project CRUD operations

### 1.5 Frontend Routing & Layout
**Duration**: 2 hours
- [ ] Install React Router v6
- [ ] Create main layout component with sidebar
- [ ] Setup routes: `/`, `/project/:id/cockpit`, `/project/:id/dashboard`
- [ ] Create navigation menu component
- [ ] Implement responsive layout (desktop-first)
- [ ] Test navigation
**Deliverable**: Basic app shell with navigation

---

## Phase 2: ReqIF Import & Data Storage (Week 3-4)

### 2.1 Parser Enhancement for Batch Processing
**Duration**: 2 hours
- [ ] Add `parse_multiple_files()` method to ReqIF parser
- [ ] Implement progress callback mechanism
- [ ] Add error collection without halting
- [ ] Create parser result summary class
- [ ] Write tests with sample ReqIF files
**Deliverable**: Enhanced parser handles multiple files with progress

### 2.2 Master Specification Import Backend
**Duration**: 2 hours
- [ ] Create `backend/import_manager.py`
- [ ] Implement `import_master_spec(project_id, file_path)` function
- [ ] Parse ReqIF, extract SPEC-OBJECTs
- [ ] Insert into `master_requirements` table (bulk insert)
- [ ] Handle duplicates (update if exists)
- [ ] Return import summary (success/warning/error counts)
**Deliverable**: Backend function imports master spec to database

### 2.3 Master Import UI - File Selection
**Duration**: 2 hours
- [ ] Create `MasterImportWizard` React component
- [ ] Implement file picker dialog (Tauri file dialog API)
- [ ] Display selected file info (name, size)
- [ ] Show loading spinner during parse
- [ ] Display import summary (requirements imported, warnings)
- [ ] Handle errors gracefully with user-friendly messages
**Deliverable**: UI for selecting and importing master spec

### 2.4 Iteration Management Backend
**Duration**: 2 hours
- [ ] Extend `import_manager.py` with iteration functions
- [ ] Implement `create_iteration(project_id, iteration_id, description)` function
- [ ] Validate iteration ID uniqueness
- [ ] Implement `list_iterations(project_id)` function
- [ ] Add `get_current_iteration()` and `set_current_iteration()`
- [ ] Write tests
**Deliverable**: Backend API for iteration management

### 2.5 Iteration Dialog UI
**Duration**: 2 hours
- [ ] Create `IterationDialog` React component (modal)
- [ ] Input field with format validation (`I-XXX_Description`)
- [ ] Check uniqueness in real-time
- [ ] Error messages for invalid format
- [ ] Integration with import workflow (blocks until iteration set)
- [ ] Iteration dropdown in toolbar (select active iteration)
**Deliverable**: Modal forces iteration ID before supplier import

# Work Breakdown Structure (WBS) - Continued

## Phase 2 (Continued): ReqIF Import & Data Storage

### 2.6 Supplier Response Import Backend
**Duration**: 2 hours
- [ ] Implement `import_supplier_feedback(project_id, iteration_id, supplier_name, file_path)` function
- [ ] Parse supplier ReqIF file using custom parser
- [ ] Match supplier requirements to master by ReqIF ID (IDENTIFIER field)
- [ ] Extract ReqIF-WF.SupplierStatus and ReqIF-WF.SupplierComment
- [ ] Handle unmatched requirements (log warning, store separately)
- [ ] Bulk insert into `supplier_feedback` table
- [ ] Return matching summary (matched/unmatched counts)
**Deliverable**: Backend imports supplier responses with matching

### 2.7 Status Harmonization Engine
**Duration**: 2 hours
- [ ] Create `backend/status_harmonizer.py` module
- [ ] Define default mapping rules (OK→Accepted, ToBeClarified→Clarification, etc.)
- [ ] Implement `normalize_status(original_status, supplier_id)` function
- [ ] Load custom mappings from `status_mappings` table
- [ ] Add fuzzy matching for common variants (case-insensitive, trim)
- [ ] Return normalized status + confidence score
- [ ] Write tests with edge cases
**Deliverable**: Status harmonization with 95%+ accuracy on test data

### 2.8 Supplier Import UI - Multi-File Selection
**Duration**: 2 hours
- [ ] Create `SupplierImportWizard` component
- [ ] Multi-file picker (select 1-20 ReqIF files)
- [ ] Display file list with remove option
- [ ] For each file, input supplier name (or auto-detect from filename)
- [ ] Show import progress (file X of Y)
- [ ] Display matching summary per supplier
- [ ] Show warnings for unmatched requirements
**Deliverable**: UI imports multiple supplier files in one session

### 2.9 Supplier Management
**Duration**: 2 hours
- [ ] Create `SuppliersPage` component
- [ ] List all suppliers for current project (table view)
- [ ] Add/edit/delete supplier
- [ ] Assign short names for grid columns (e.g., "BOSCH" → "BSH")
- [ ] Configure status mappings per supplier (advanced modal)
- [ ] Persist to `suppliers` and `status_mappings` tables
**Deliverable**: Supplier management UI with custom mappings

---

## Phase 3: Requirements Cockpit View (Week 5-7)

### 3.1 Data Loading Service
**Duration**: 2 hours
- [ ] Create `backend/cockpit_data_service.py`
- [ ] Implement `get_cockpit_data(project_id, iteration_id, filters)` function
- [ ] Join master_requirements + supplier_feedback for active iteration
- [ ] Apply filters (status, text search)
- [ ] Return JSON structure: `{requirements: [{id, reqif_id, text, suppliers: [{name, status, comment}]}]}`
- [ ] Optimize query with indexes
- [ ] Test performance with 500 requirements × 10 suppliers (< 2 sec)
**Deliverable**: API returns grid-ready data in < 2 seconds

### 3.2 Grid Component Selection & Setup
**Duration**: 2 hours
- [ ] Evaluate AG Grid Community vs TanStack Table v8
- [ ] **Decision**: Use AG Grid (frozen columns, enterprise-grade performance)
- [ ] Install `ag-grid-react` and `ag-grid-community`
- [ ] Create `CockpitGrid` component (wrapper)
- [ ] Setup basic column definitions
- [ ] Enable row virtualization
- [ ] Test rendering 500 rows
**Deliverable**: AG Grid renders test data smoothly

### 3.3 Column Definition & Frozen Columns
**Duration**: 2 hours
- [ ] Define column structure: `[reqif_id, master_text, ...supplier columns]`
- [ ] Set first 2 columns as pinned (`pinned: 'left'`)
- [ ] Dynamic supplier columns (generate from data)
- [ ] Column format: `Supplier_Name_Status | Supplier_Name_Comment`
- [ ] Auto-size columns on initial load
- [ ] Add column resizing handles
**Deliverable**: Grid with frozen ReqIF ID + Master Text columns

### 3.4 Status Badge Cell Renderer
**Duration**: 2 hours
- [ ] Create custom cell renderer for status columns
- [ ] Render colored badge: Accepted (green), Clarification (yellow), Rejected (red)
- [ ] Handle null/empty statuses (gray "Not Set" badge)
- [ ] Add tooltip showing original status value
- [ ] Ensure badges are visually distinct (icons + colors)
- [ ] Test with colorblind-safe palette
**Deliverable**: Status cells show colored badges

### 3.5 Conflict Detection Backend
**Duration**: 2 hours
- [ ] Create `backend/conflict_detector.py`
- [ ] Implement `detect_conflicts(cockpit_data)` function
- [ ] Logic: Flag row if 2+ suppliers have different negative statuses (Yellow/Red combinations)
- [ ] Return list of requirement IDs with conflicts
- [ ] Calculate conflict details (which suppliers disagree)
- [ ] Write unit tests with edge cases
**Deliverable**: Conflict detection returns accurate results

### 3.6 Conflict Highlighting in Grid
**Duration**: 2 hours
- [ ] Extend `get_cockpit_data()` to include `is_conflict` flag
- [ ] Apply row styling based on conflict flag (`getRowClass`)
- [ ] Conflict rows: amber/orange background (#FFF3CD)
- [ ] Add conflict icon in first column (cell renderer)
- [ ] Highlight conflict icon in row header
- [ ] Test visibility in grid
**Deliverable**: Conflict rows visually highlighted

### 3.7 Text Search & Filtering
**Duration**: 2 hours
- [ ] Create `FilterToolbar` component above grid
- [ ] Text input with debounced search (300ms)
- [ ] Search ReqIF ID and Master Text fields
- [ ] Status filter dropdown (Accepted/Clarification/Rejected/Conflict/All)
- [ ] Supplier visibility toggles (show/hide columns)
- [ ] "Clear All Filters" button
- [ ] Update grid data via AG Grid filter API
**Deliverable**: Working search and filter controls

### 3.8 Grid Context Menu & Actions
**Duration**: 2 hours
- [ ] Enable AG Grid context menu (right-click)
- [ ] Menu items: "View Details", "Copy ReqIF ID", "View History", "Make Decision"
- [ ] Implement "View Details" modal (shows all attributes)
- [ ] Copy ReqIF ID to clipboard
- [ ] Hook up other actions (placeholders for now)
- [ ] Test menu on Windows and macOS
**Deliverable**: Context menu with basic actions

### 3.9 Grid Performance Optimization
**Duration**: 2 hours
- [ ] Enable AG Grid row buffer (50 rows)
- [ ] Setup lazy loading for > 500 rows (pagination)
- [ ] Debounce filter updates (300ms)
- [ ] Measure render time with Chrome DevTools
- [ ] Profile memory usage with 1000 rows
- [ ] Optimize re-renders (React.memo, useMemo)
- [ ] Document performance metrics
**Deliverable**: Grid loads < 2 sec, scrolls at 60fps

---

## Phase 4: Dashboard & Analytics (Week 8)

### 4.1 Dashboard Data Service
**Duration**: 2 hours
- [ ] Create `backend/dashboard_service.py`
- [ ] Implement `get_dashboard_metrics(project_id, iteration_id)` function
- [ ] Calculate: Total Requirements, Accepted Count, Clarification Count, Rejected Count, Conflicts Count
- [ ] Calculate percentages
- [ ] Return JSON structure
- [ ] Cache metrics per iteration (invalidate on new import)
- [ ] Test with various data scenarios
**Deliverable**: API returns dashboard metrics in < 500ms

### 4.2 KPI Cards Component
**Duration**: 2 hours
- [ ] Create `DashboardPage` component
- [ ] Create `KPICard` sub-component (reusable)
- [ ] Display 5 cards: Total, Accepted (green), Clarification (yellow), Rejected (red), Conflicts (amber)
- [ ] Show count and percentage
- [ ] Click card to filter grid to that status (navigation)
- [ ] Responsive grid layout (2-3 cards per row)
**Deliverable**: Dashboard shows KPI cards with live data

### 4.3 Supplier Comparison Chart Backend
**Duration**: 2 hours
- [ ] Extend `dashboard_service.py`
- [ ] Implement `get_supplier_comparison(project_id, iteration_id)` function
- [ ] For each supplier: calculate % Accepted, % Clarification, % Rejected
- [ ] Sort by Accepted % (descending)
- [ ] Return JSON array: `[{supplier, accepted_pct, clarification_pct, rejected_pct}]`
- [ ] Test with 10 suppliers
**Deliverable**: API returns supplier comparison data

### 4.4 Supplier Comparison Chart UI
**Duration**: 2 hours
- [ ] Install Recharts: `npm install recharts`
- [ ] Create `SupplierComparisonChart` component
- [ ] Implement horizontal stacked bar chart
- [ ] X-axis: Percentage (0-100%)
- [ ] Y-axis: Supplier names
- [ ] Segments: Green (Accepted), Yellow (Clarification), Red (Rejected)
- [ ] Hover tooltip shows exact counts
- [ ] Legend below chart
**Deliverable**: Chart visualizes supplier acceptance rates

### 4.5 Dashboard Auto-Refresh
**Duration**: 2 hours
- [ ] Implement dashboard data fetching on iteration change
- [ ] Add manual refresh button (icon button)
- [ ] Show loading skeleton while fetching
- [ ] Handle errors gracefully
- [ ] Animate metric changes (count-up effect)
- [ ] Test with rapid iteration switching
**Deliverable**: Dashboard updates when iteration changes

---

## Phase 5: Decision Making & Export (Week 9)

### 5.1 Decision Logging Backend
**Duration**: 2 hours
- [ ] Create `backend/decision_manager.py`
- [ ] Implement `save_decision(master_req_id, iteration_id, status, note, user)` function
- [ ] Insert into `custre_decisions` table
- [ ] Handle update if decision already exists
- [ ] Implement `get_decision(master_req_id, iteration_id)` function
- [ ] Return decision with timestamp
- [ ] Write tests
**Deliverable**: Backend saves and retrieves decisions

### 5.2 Decision Panel UI
**Duration**: 2 hours
- [ ] Create `DecisionPanel` component (sidebar or modal)
- [ ] Show when row selected in grid
- [ ] Display: ReqIF ID, Master Text, all supplier responses
- [ ] Decision status dropdown: Accepted/Rejected/Modified/Deferred
- [ ] Action Note textarea (max 2000 chars, char counter)
- [ ] Save button (calls backend)
- [ ] Show existing decision if present
- [ ] Success/error toast notifications
**Deliverable**: UI for logging decisions

### 5.3 Decision History Backend
**Duration**: 2 hours
- [ ] Extend `decision_manager.py`
- [ ] Implement `get_decision_history(master_req_id)` function
- [ ] Return all decisions across iterations (sorted by date)
- [ ] Include: iteration_id, date, user, status, note
- [ ] Test with multiple iterations
**Deliverable**: API returns decision history

### 5.4 Decision History Modal
**Duration**: 2 hours
- [ ] Create `DecisionHistoryModal` component
- [ ] Table view: Iteration | Date | User | Decision | Note
- [ ] Sortable by date (default: newest first)
- [ ] Filter by decision status (optional)
- [ ] Export history to CSV button
- [ ] Open from grid context menu ("View History")
**Deliverable**: Modal shows decision timeline

### 5.5 Bulk Decision Operations
**Duration**: 2 hours
- [ ] Add row selection to grid (checkboxes)
- [ ] Create `BulkActionsToolbar` component (appears when rows selected)
- [ ] Actions: Accept All, Reject All, Mark for Clarification
- [ ] Confirmation dialog shows count
- [ ] Call backend in batch (single transaction)
- [ ] Show progress spinner
- [ ] Refresh grid after completion
**Deliverable**: Bulk actions work for 100+ rows in < 2 sec

### 5.6 CSV/XLSX Export Backend
**Duration**: 2 hours
- [ ] Create `backend/export_manager.py`
- [ ] Implement `export_to_csv(project_id, iteration_id, filters, output_path)` function
- [ ] Format: ReqIF ID | Master Text | Supplier1 Status | Supplier1 Comment | ... | CustRE Decision | Action Note
- [ ] Apply current filters
- [ ] Use `pandas.to_csv()`
- [ ] Implement `export_to_xlsx()` with formatting (frozen header, auto-width)
- [ ] Test with 500 requirements × 10 suppliers (< 5 sec)
**Deliverable**: Backend exports to CSV and XLSX

### 5.7 Export UI
**Duration**: 2 hours
- [ ] Create `ExportDialog` component (modal)
- [ ] Radio buttons: CSV / XLSX
- [ ] Checkbox: "Apply current filters" (default: checked)
- [ ] File picker for output location
- [ ] Export button (calls backend)
- [ ] Progress bar during export
- [ ] Success message with "Open File" button
- [ ] Handle errors (disk full, permissions)
**Deliverable**: UI exports data to user-selected location

---

## Phase 6: Polish & Testing (Week 10-12)

### 6.1 Error Handling & Validation
**Duration**: 2 hours
- [ ] Add try-catch blocks to all backend functions
- [ ] Return structured error objects: `{success: bool, error: str, details: dict}`
- [ ] Frontend displays errors in user-friendly format (toast, modal)
- [ ] Validate all user inputs (iteration ID format, file paths, etc.)
- [ ] Handle corrupt ReqIF files gracefully (log error, continue)
- [ ] Test error scenarios (invalid file, disk full, etc.)
**Deliverable**: Robust error handling across app

### 6.2 Loading States & Progress Indicators
**Duration**: 2 hours
- [ ] Add loading spinners to all async operations
- [ ] Import progress: show "Importing X of Y files..."
- [ ] Grid loading: skeleton rows
- [ ] Dashboard loading: skeleton cards
- [ ] Disable buttons during operations
- [ ] Ensure UI remains responsive (no freezing)
**Deliverable**: Clear feedback for all long-running operations

### 6.3 Keyboard Shortcuts
**Duration**: 2 hours
- [ ] Implement global keyboard shortcuts
  - `Ctrl/Cmd + I`: Open Import Dialog
  - `Ctrl/Cmd + E`: Export
  - `Ctrl/Cmd + F`: Focus Search
  - `Ctrl/Cmd + D`: Make Decision (when row selected)
  - `Escape`: Close modals
- [ ] Show shortcuts in tooltips
- [ ] Create "Keyboard Shortcuts" help modal (`Ctrl/Cmd + /`)
- [ ] Test on Windows and macOS
**Deliverable**: Common actions accessible via keyboard

### 6.4 Onboarding Wizard
**Duration**: 2 hours
- [ ] Create `OnboardingWizard` component (first launch only)
- [ ] Step 1: Welcome + tool overview (30 sec read)
- [ ] Step 2: Create first project (interactive)
- [ ] Step 3: Import master spec (interactive)
- [ ] "Skip" and "Next" buttons
- [ ] Store completion in settings (don't show again)
- [ ] Test full flow
**Deliverable**: 3-step onboarding for new users

### 6.5 Settings & Preferences
**Duration**: 2 hours
- [ ] Create `SettingsPage` component
- [ ] Section: General (app theme, auto-backup on/off)
- [ ] Section: Import (default iteration ID prefix, status mapping presets)
- [ ] Section: Grid (row height, font size, color scheme)
- [ ] Section: Privacy (telemetry toggle - off by default)
- [ ] Save to local JSON file or SQLite settings table
- [ ] Test persistence across restarts
**Deliverable**: Settings page with 10+ options

### 6.6 Unit Testing - Backend
**Duration**: 2 hours
- [ ] Setup pytest framework
- [ ] Write tests for `project_manager.py` (create, open, list)
- [ ] Write tests for `import_manager.py` (master, supplier imports)
- [ ] Write tests for `status_harmonizer.py` (mapping edge cases)
- [ ] Write tests for `conflict_detector.py` (various scenarios)
- [ ] Aim for 80% code coverage
- [ ] Run tests in CI pipeline (GitHub Actions)
**Deliverable**: 50+ backend unit tests passing

### 6.7 Integration Testing
**Duration**: 2 hours
- [ ] Create end-to-end test scenarios
- [ ] Test 1: Create project → Import master → Import 3 suppliers → View grid
- [ ] Test 2: Make decisions → Export → Verify CSV content
- [ ] Test 3: Multiple iterations → Switch between → Verify data isolation
- [ ] Use real ReqIF sample files
- [ ] Automate with Playwright or Tauri's test framework
- [ ] Document test cases
**Deliverable**: 3 full integration tests passing

### 6.8 Performance Testing & Profiling
**Duration**: 2 hours
- [ ] Test with large dataset: 1000 requirements × 15 suppliers
- [ ] Measure import time, grid load time, export time
- [ ] Profile database queries (identify slow queries)
- [ ] Profile React renders (identify re-render bottlenecks)
- [ ] Optimize if needed (add indexes, memoization)
- [ ] Document performance benchmarks
**Deliverable**: App meets all performance targets

### 6.9 User Acceptance Testing (UAT)
**Duration**: 2 hours
- [ ] Recruit 3-5 target users (CustREs)
- [ ] Prepare UAT script (realistic tasks)
- [ ] Observe users completing tasks (screen recording)
- [ ] Collect feedback (survey, interview)
- [ ] Identify usability issues
- [ ] Prioritize fixes
- [ ] Implement critical UAT feedback
**Deliverable**: UAT report with user feedback

### 6.10 Bug Fixing Sprint
**Duration**: 6-8 hours (3-4 tasks × 2 hours each)
- [ ] Fix all P0 (critical) bugs
- [ ] Fix high-priority P1 bugs
- [ ] Triage P2/P3 bugs (defer if not blocking)
- [ ] Regression testing after fixes
- [ ] Update test suite to prevent regressions
**Deliverable**: Zero P0 bugs, < 5 P1 bugs

### 6.11 Documentation - User Guide
**Duration**: 2 hours
- [ ] Write user guide (Markdown or PDF)
- [ ] Sections: Installation, Quick Start, Importing Files, Using Cockpit, Making Decisions, Exporting
- [ ] Screenshots for each major step
- [ ] Troubleshooting section (common issues)
- [ ] FAQ (5-10 questions)
- [ ] Host on GitHub Pages or bundle with app
**Deliverable**: 15-page user guide with screenshots

### 6.12 Documentation - Technical
**Duration**: 2 hours
- [ ] Write architecture document (Markdown)
- [ ] Database schema diagram (ERD)
- [ ] API documentation (backend functions)
- [ ] ReqIF parser usage guide
- [ ] Deployment instructions (build, test, package)
- [ ] Contributing guidelines (for future developers)
**Deliverable**: Technical docs for developers

---

## Phase 7: Release Preparation (Week 12)

### 7.1 Build Configuration
**Duration**: 2 hours
- [ ] Configure Tauri bundler settings (tauri.conf.json)
- [ ] Set app name, version, identifier
- [ ] Configure bundle targets: MSI (Windows), DMG (macOS)
- [ ] Set app icon (generate all sizes)
- [ ] Configure auto-updater (optional, V2.0 feature)
- [ ] Test build on Windows and macOS
**Deliverable**: Build configuration for release

### 7.2 Windows Installer Creation
**Duration**: 2 hours
- [ ] Run `tauri build` on Windows machine
- [ ] Test MSI installer (install, run, uninstall)
- [ ] Verify file associations (.sqlite)
- [ ] Check Start Menu shortcut
- [ ] Test on clean Windows 10 and Windows 11 machines
- [ ] Sign installer (optional, requires code signing cert)
**Deliverable**: Windows MSI installer (< 50MB)

### 7.3 macOS Installer Creation
**Duration**: 2 hours
- [ ] Run `tauri build` on macOS machine (Intel and Apple Silicon)
- [ ] Test DMG installer (mount, drag to Applications, run)
- [ ] Verify app permissions (file system access)
- [ ] Test on macOS 12 and 13
- [ ] Notarize app with Apple (required for distribution)
**Deliverable**: macOS DMG installer (< 50MB)

### 7.4 Release Notes & Changelog
**Duration**: 1 hour
- [ ] Write v1.0 release notes
- [ ] Highlight key features (5-10 bullets)
- [ ] List known issues (if any)
- [ ] System requirements (OS versions)
- [ ] Installation instructions
- [ ] Changelog format for future versions
**Deliverable**: RELEASE_NOTES.md

### 7.5 GitHub Release
**Duration**: 1 hour
- [ ] Create GitHub Release (tag: v1.0.0)
- [ ] Upload Windows MSI
- [ ] Upload macOS DMG (Intel and Apple Silicon)
- [ ] Attach user guide PDF
- [ ] Add release notes to GitHub Release description
- [ ] Set as "Latest Release"
**Deliverable**: Public GitHub Release v1.0.0

### 7.6 Internal Launch
**Duration**: 2 hours
- [ ] Send launch email to target users (CustREs, managers)
- [ ] Include download links
- [ ] Schedule 1-hour kickoff webinar (demo + Q&A)
- [ ] Setup support channel (Slack, Teams, or email)
- [ ] Monitor early adopter feedback (first 48 hours)
- [ ] Be ready for hotfix if critical bug found
**Deliverable**: 20+ users onboarded in first week

---

## Enterprise Add-Ons (Post-MVP, Prioritized)

### Add-On 1: Database Encryption
**Duration**: 4 hours
- [ ] Research SQLCipher integration
- [ ] Implement password dialog on project open
- [ ] Encrypt new projects by default
- [ ] Migration tool for existing projects (encrypt in-place)
- [ ] Key derivation (PBKDF2, 10,000 rounds)
- [ ] Test performance impact (< 10% overhead)
**Deliverable**: AES-256 encrypted SQLite files

### Add-On 2: Nexus/Artifactory Backup Integration
**Duration**: 6 hours
- [ ] Design backup workflow (manual and auto)
- [ ] Implement Nexus REST API client
- [ ] Upload `.sqlite` file to Nexus on-demand
- [ ] Auto-backup after each import (optional setting)
- [ ] Version tracking (semantic versioning)
- [ ] Restore from Nexus feature
**Deliverable**: Automated versioned backups to artifact repository

### Add-On 3: ReqIF Roundtrip Export
**Duration**: 8 hours
- [ ] Study OMG ReqIF standard (chapter 7.4)
- [ ] Implement ReqIF generator (inverse of parser)
- [ ] Generate new ReqIF with CustRE decisions
- [ ] Map decisions to ReqIF-WF.CustomerStatus
- [ ] Include all original attributes + new decisions
- [ ] Validate output with ReqIF schema
- [ ] Test import into DOORS, Polarion
**Deliverable**: Export CustRE decisions as valid ReqIF file

### Add-On 4: Full XHTML Rendering
**Duration**: 8 hours
- [ ] Research safe XHTML rendering (DOMPurify)
- [ ] Implement custom cell renderer for rich text
- [ ] Handle embedded images (Base64 or external)
- [ ] Handle tables, lists, formatting
- [ ] Sanitize malicious XHTML
- [ ] Test with real vendor ReqIF files (BMW, VW, Bosch)
- [ ] Performance testing (rich text slows rendering)
**Deliverable**: Grid displays formatted requirement text

### Add-On 5: Multi-User Collaboration (SQLite Shared Mode)
**Duration**: 12 hours
- [ ] Enable SQLite WAL mode (Write-Ahead Logging)
- [ ] Implement row-level locking (pessimistic)
- [ ] Show "Locked by User X" indicator
- [ ] Real-time update notifications (polling or WebSocket)
- [ ] Conflict resolution for simultaneous edits
- [ ] Test with 5 concurrent users
- [ ] Network share setup guide (Windows/macOS)
**Deliverable**: Multiple CustREs work on same project simultaneously

### Add-On 6: Advanced Analytics Dashboard
**Duration**: 6 hours
- [ ] Iteration comparison chart (trend over time)
- [ ] Requirement complexity metrics (text length, attribute count)
- [ ] Supplier response time tracking (if timestamps available)
- [ ] Heatmap: Supplier vs Status (which suppliers struggle most)
- [ ] Export charts as PNG/PDF
- [ ] Drill-down filters (click chart → filter grid)
**Deliverable**: 5+ new analytics visualizations

### Add-On 7: Email Notifications
**Duration**: 4 hours
- [ ] Integrate SMTP client (nodemailer or Python smtplib)
- [ ] Trigger: Send email on import completion
- [ ] Email content: Import summary, conflict count, link to project
- [ ] User settings: Email address, SMTP server config
- [ ] Test with Gmail, Outlook, corporate SMTP
**Deliverable**: Automated email alerts for key events

### Add-On 8: PDF Report Generation
**Duration**: 6 hours
- [ ] Integrate PDF library (jsPDF or Python ReportLab)
- [ ] Design professional report template
- [ ] Sections: Cover, Executive Summary, Dashboard Metrics, Supplier Comparison, Conflict List, Detailed Table
- [ ] Embed charts as images
- [ ] Generate PDF in < 10 seconds
- [ ] Test with 500 requirements
**Deliverable**: One-click PDF report for stakeholders

### Add-On 9: AI-Powered Insights (Future Vision)
**Duration**: 20+ hours
- [ ] Integrate local LLM (Ollama + Llama 3)
- [ ] Feature: Natural language query ("Show me all rejected safety requirements")
- [ ] Feature: Auto-suggest clarification text based on supplier comment
- [ ] Feature: Conflict prediction (ML model trained on historical data)
- [ ] Privacy: All processing local (no external API calls)
- [ ] Test accuracy with real data
**Deliverable**: AI assistant for CustREs

### Add-On 10: DOORS/Polarion Connector
**Duration**: 12 hours
- [ ] Research DOORS API (DXL scripting)
- [ ] Implement direct import from DOORS module
- [ ] Export decisions back to DOORS
- [ ] Same for Polarion (REST API)
- [ ] Handle authentication (OAuth, API keys)
- [ ] Test with real DOORS/Polarion instances
**Deliverable**: Native integration with enterprise RM tools

---

## Summary

**Total MVP Effort**: ~120 hours (6 weeks with 1 developer, or 3 weeks with 2 developers)

**MVP Task Count**: 60 tasks × 2 hours each = 120 hours

**Enterprise Add-Ons**: Additional 80+ hours (phased rollout in V2.0-V3.0)

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (no parallelization)

**Risk Mitigation**: Phases 4-5 can start once Phase 3 Week 1 is complete (partial parallelization)

**Recommended Team**: 2 developers (1 frontend + React, 1 backend + Python) + 0.5 QA

---

## Delivery Timeline

- **Week 1-2**: Infrastructure ✅
- **Week 3-4**: Import & Storage ✅
- **Week 5-7**: Cockpit View (core feature) ✅
- **Week 8**: Dashboard ✅
- **Week 9**: Decisions & Export ✅
- **Week 10-11**: Testing & Polish ✅
- **Week 12**: Release 🚀

**Target Release Date**: End of Week 12 (Q2 2026)

---

This WBS provides:
1. ✅ Every task completable in ~2 hours
2. ✅ Clear deliverables
3. ✅ Logical dependency chain
4. ✅ Enterprise features as optional add-ons
5. ✅ Realistic timeline for MVP launch
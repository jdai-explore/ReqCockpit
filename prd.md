# Product Requirements Document (PRD)
## ReqCockpit: Multi-Partner Requirements Aggregation Tool (Python Edition)

| Attribute | Value |
|:---|:---|
| **Product Name** | **ReqCockpit** |
| **Version** | 1.0 (MVP) |
| **Document Version** | 3.0 - Python Native |
| **Target Release** | Q2 2026 |
| **Status** | Ready for Development |

---

## 1. Executive Summary

### 1.1 Vision Statement
ReqCockpit revolutionizes the Stakeholder Request Clarification (SRC) process in automotive supply chains by providing a **privacy-first, high-performance desktop application** that enables Customer Requirements Engineers (CustREs) to aggregate, compare, and resolve supplier feedback across multiple iterations.

### 1.2 Solution Overview
ReqCockpit provides:
1. **Automated Multi-Supplier Aggregation**: Import ReqIF files, align by ReqIF ID, display side-by-side
2. **Privacy-First Architecture**: 100% local processing with SQLite storage
3. **Iteration-Based Audit Trail**: Tag each import, maintain complete time-series history
4. **Conflict Detection Engine**: Automatically flag supplier disagreements
5. **Fast Performance**: Sub-5-second load times for 500+ requirements

---

## 2. Revised Technology Stack

**Application Framework:**
- **GUI Framework**: PyQt6 (modern, native, cross-platform)
- **Language**: Python 3.11+
- **Database**: SQLite 3.x with SQLAlchemy 2.x
- **Data Grid**: QTableWidget with custom optimizations
- **Charts**: matplotlib (embedded in PyQt6)
- **ReqIF Parser**: Custom parser (provided, enhanced)

**Distribution:**
- **Packaging**: PyInstaller (single executable)
- **Platforms**: Windows 10/11, macOS 12+
- **Size Target**: < 80MB executable

**Key Libraries:**
```
PyQt6>=6.6.0
SQLAlchemy>=2.0.0
pandas>=2.0.0
matplotlib>=3.8.0
openpyxl>=3.1.0
PyInstaller>=6.0.0
```

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Presentation Layer (PyQt6)              │
│                                                      │
│  MainWindow + ProjectManager + CockpitView          │
│  + DashboardView + Dialogs                          │
│                                                      │
│  - QTableWidget (requirements grid)                 │
│  - QCharts/matplotlib (analytics)                   │
│  - Custom widgets and delegates                     │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│          Business Logic Layer (Python)               │
│                                                      │
│  Services: ImportService, ConflictDetector,         │
│           StatusHarmonizer, ExportService           │
│                                                      │
│  - ReqIF file parsing                               │
│  - Data transformation and aggregation              │
│  - Business rules and validation                    │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│          Data Access Layer (SQLAlchemy)              │
│                                                      │
│  Models: Project, Iteration, MasterRequirement,     │
│          SupplierFeedback, CustREDecision           │
│                                                      │
│  - Database operations                              │
│  - Query optimization                               │
│  - Transaction management                           │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│              Data Persistence Layer                  │
│                                                      │
│  SQLite Database ([ProjectName].sqlite)             │
└─────────────────────────────────────────────────────┘
```

---

## 4. Project Structure

```
reqcockpit/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
│
├── models/                     # SQLAlchemy models
│   ├── __init__.py
│   ├── base.py                # Base model class
│   ├── project.py             # Project model
│   ├── iteration.py           # Iteration model
│   ├── requirement.py         # Master requirement model
│   ├── feedback.py            # Supplier feedback model
│   ├── decision.py            # CustRE decision model
│   └── supplier.py            # Supplier model
│
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── database_service.py    # Database operations
│   ├── import_service.py      # ReqIF import logic
│   ├── export_service.py      # Export functionality
│   ├── conflict_detector.py   # Conflict detection
│   ├── status_harmonizer.py   # Status normalization
│   └── analytics_service.py   # Dashboard metrics
│
├── parsers/                    # ReqIF parsing
│   ├── __init__.py
│   └── reqif_parser.py        # Enhanced ReqIF parser
│
├── ui/                         # PyQt6 UI components
│   ├── __init__.py
│   ├── main_window.py         # Main application window
│   ├── project_dialog.py      # Project management dialogs
│   ├── import_wizard.py       # Import wizard
│   ├── cockpit_view.py        # Requirements comparison grid
│   ├── dashboard_view.py      # Analytics dashboard
│   ├── decision_panel.py      # Decision making panel
│   ├── widgets/               # Custom widgets
│   │   ├── __init__.py
│   │   ├── status_badge.py   # Status badge widget
│   │   ├── filter_bar.py     # Filter toolbar
│   │   └── iteration_selector.py
│   └── dialogs/               # Dialog windows
│       ├── __init__.py
│       ├── iteration_dialog.py
│       ├── decision_history_dialog.py
│       └── export_dialog.py
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── constants.py           # Constants and enums
│   ├── validators.py          # Input validation
│   └── formatters.py          # Data formatting
│
├── resources/                  # Application resources
│   ├── icons/                 # Icon files
│   ├── styles/                # QSS stylesheets
│   └── templates/             # Report templates
│
└── tests/                      # Unit and integration tests
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    ├── test_parser.py
    └── fixtures/              # Test ReqIF files
```

---

## 5. Development Phases (Revised for Python)

### Phase 1: Core Infrastructure (Week 1-2)
- Database models and migrations
- Basic PyQt6 window structure
- Project CRUD operations

### Phase 2: ReqIF Import (Week 3-4)
- Parser integration
- Master spec import
- Supplier response import with iteration tagging
- Status harmonization

### Phase 3: Cockpit View (Week 5-7)
- QTableWidget with frozen columns
- Status badges and conflict highlighting
- Filtering and search
- Performance optimization

### Phase 4: Dashboard (Week 8)
- KPI cards
- Supplier comparison charts
- Iteration timeline

### Phase 5: Decision & Export (Week 9)
- Decision logging UI
- Bulk operations
- CSV/XLSX export

### Phase 6: Polish & Testing (Week 10-12)
- Error handling
- User testing
- Documentation
- Packaging with PyInstaller

---

## 6. Key Functional Requirements

### Core Features (P0 - MVP)
- ✅ Project creation and management
- ✅ Master specification import
- ✅ Iteration-based supplier response import
- ✅ Side-by-side comparison grid with frozen columns
- ✅ Automatic status harmonization
- ✅ Conflict detection and highlighting
- ✅ Text search and filtering
- ✅ CustRE decision logging
- ✅ Dashboard with KPIs
- ✅ Export to CSV/XLSX

### Enhanced Features (P1 - Post-MVP)
- Supplier comparison charts
- Bulk decision operations
- Decision history tracking
- PDF report generation
- Keyboard shortcuts

---

## 7. Performance Targets

| Metric | Target |
|:---|:---|
| Master Import | < 10 sec (500 reqs) |
| Supplier Import | < 5 sec per supplier |
| Grid Load | < 2 sec (500 reqs × 10 suppliers) |
| Search/Filter | < 200ms |
| Export | < 5 sec |

---

## 8. Success Criteria

**MVP Launch:**
- Import and aggregate 10+ supplier responses
- Display 500+ requirements smoothly
- Zero data corruption
- All P0 features working
- < 5 critical bugs

**Month 1 Post-Launch:**
- 80% user adoption
- 50+ projects created
- 40% reduction in SRC cycle time
- User satisfaction > 4.0/5.0

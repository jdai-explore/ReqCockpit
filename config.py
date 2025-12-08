"""
Configuration settings for ReqCockpit application
"""
import os
from pathlib import Path
from enum import Enum

# Application Info
APP_NAME = "ReqCockpit"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Requirements Engineering Team"
ORGANIZATION = "Automotive Systems"

# Paths
BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"
TEMPLATES_DIR = RESOURCES_DIR / "templates"

# User directories
USER_HOME = Path.home()
APP_DATA_DIR = USER_HOME / ".reqcockpit"
APP_DATA_DIR.mkdir(exist_ok=True)

RECENT_PROJECTS_FILE = APP_DATA_DIR / "recent_projects.json"
SETTINGS_FILE = APP_DATA_DIR / "settings.json"

# Database
DB_EXTENSION = ".sqlite"
BACKUP_EXTENSION = ".sqlite.backup"
MAX_RECENT_PROJECTS = 10

# Import Settings
DEFAULT_ITERATION_PREFIX = "I-"
MAX_SUPPLIERS_PER_VIEW = 20
BATCH_IMPORT_SIZE = 100

# Performance
GRID_PAGE_SIZE = 100
SEARCH_DEBOUNCE_MS = 300
MAX_GRID_ROWS_BEFORE_PAGINATION = 500

# Status Normalization
class NormalizedStatus(Enum):
    ACCEPTED = "Accepted"
    CLARIFICATION = "Clarification Needed"
    REJECTED = "Rejected"
    NOT_SET = "Not Set"

STATUS_COLORS = {
    NormalizedStatus.ACCEPTED: "#28a745",      # Green
    NormalizedStatus.CLARIFICATION: "#ffc107",  # Yellow
    NormalizedStatus.REJECTED: "#dc3545",      # Red
    NormalizedStatus.NOT_SET: "#6c757d"        # Gray
}

# Default status mappings (supplier-specific mappings override these)
DEFAULT_STATUS_MAPPINGS = {
    # Accepted variants
    "ok": NormalizedStatus.ACCEPTED,
    "accepted": NormalizedStatus.ACCEPTED,
    "agreed": NormalizedStatus.ACCEPTED,
    "compliant": NormalizedStatus.ACCEPTED,
    "confirmed": NormalizedStatus.ACCEPTED,
    "yes": NormalizedStatus.ACCEPTED,
    
    # Clarification variants
    "needs clarification": NormalizedStatus.CLARIFICATION,
    "tobeclarified": NormalizedStatus.CLARIFICATION,
    "to be clarified": NormalizedStatus.CLARIFICATION,
    "unclear": NormalizedStatus.CLARIFICATION,
    "question": NormalizedStatus.CLARIFICATION,
    "pending": NormalizedStatus.CLARIFICATION,
    
    # Rejected variants
    "not accepted": NormalizedStatus.REJECTED,
    "rejected": NormalizedStatus.REJECTED,
    "notagreed": NormalizedStatus.REJECTED,
    "not agreed": NormalizedStatus.REJECTED,
    "declined": NormalizedStatus.REJECTED,
    "no": NormalizedStatus.REJECTED,
    "nok": NormalizedStatus.REJECTED,
}

# Conflict Detection
CONFLICT_COLOR = "#fff3cd"  # Amber background
CONFLICT_ICON = "⚠"

# Decision Statuses
class DecisionStatus(Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    MODIFIED = "Modified"
    DEFERRED = "Deferred"

# Export Settings
EXPORT_FORMATS = ["csv", "xlsx"]
MAX_EXCEL_ROWS = 1000000  # Excel limit
EXCEL_SHEET_NAME = "Requirements"

# UI Settings
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
GRID_ROW_HEIGHT = 35
FROZEN_COLUMNS_COUNT = 2  # ReqIF ID + Master Text

# Validation
ITERATION_ID_PATTERN = r'^I-\d{3}_[\w\-]+$'
MAX_ACTION_NOTE_LENGTH = 2000
MAX_SUPPLIER_NAME_LENGTH = 100

# Logging
LOG_FILE = APP_DATA_DIR / "reqcockpit.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

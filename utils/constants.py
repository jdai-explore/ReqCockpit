"""
Constants and enumerations for ReqCockpit
"""
from enum import Enum
from config import NormalizedStatus, DecisionStatus, STATUS_COLORS


class StatusLabel(Enum):
    """User-friendly labels for normalized statuses"""
    ACCEPTED = "✓ Accepted"
    CLARIFICATION = "? Clarification Needed"
    REJECTED = "✗ Rejected"
    NOT_SET = "- Not Set"


class DecisionLabel(Enum):
    """User-friendly labels for decision statuses"""
    ACCEPTED = "✓ Accepted"
    REJECTED = "✗ Rejected"
    MODIFIED = "◆ Modified"
    DEFERRED = "⏱ Deferred"


# Mapping from normalized status to display label
STATUS_LABELS = {
    NormalizedStatus.ACCEPTED.value: StatusLabel.ACCEPTED.value,
    NormalizedStatus.CLARIFICATION.value: StatusLabel.CLARIFICATION.value,
    NormalizedStatus.REJECTED.value: StatusLabel.REJECTED.value,
    NormalizedStatus.NOT_SET.value: StatusLabel.NOT_SET.value,
}

# Mapping from decision status to display label
DECISION_LABELS = {
    DecisionStatus.ACCEPTED.value: DecisionLabel.ACCEPTED.value,
    DecisionStatus.REJECTED.value: DecisionLabel.REJECTED.value,
    DecisionStatus.MODIFIED.value: DecisionLabel.MODIFIED.value,
    DecisionStatus.DEFERRED.value: DecisionLabel.DEFERRED.value,
}

# Color mapping for UI display
STATUS_DISPLAY_COLORS = STATUS_COLORS

# Icon mappings
STATUS_ICONS = {
    NormalizedStatus.ACCEPTED.value: "✓",
    NormalizedStatus.CLARIFICATION.value: "?",
    NormalizedStatus.REJECTED.value: "✗",
    NormalizedStatus.NOT_SET.value: "-",
}

# Keyboard shortcuts
SHORTCUTS = {
    'new_project': 'Ctrl+N',
    'open_project': 'Ctrl+O',
    'import_master': 'Ctrl+I',
    'import_supplier': 'Ctrl+Shift+I',
    'export': 'Ctrl+E',
    'search': 'Ctrl+F',
    'refresh': 'F5',
    'quit': 'Ctrl+Q',
}

# Default column widths for grid (in pixels)
GRID_COLUMN_WIDTHS = {
    'reqif_id': 120,
    'master_text': 300,
    'supplier_feedback': 150,
    'decision': 120,
}

# Pagination settings
ROWS_PER_PAGE = 100
MAX_VISIBLE_PAGES = 5

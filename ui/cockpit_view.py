"""
Cockpit view - Requirements comparison grid
"""
import logging
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor

from models.base import db_manager
from models.requirement import MasterRequirement
from models.feedback import SupplierFeedback
from models.supplier import Supplier
from config import STATUS_COLORS, NormalizedStatus, FROZEN_COLUMNS_COUNT, CONFLICT_COLOR
from services.conflict_detector import conflict_detector

logger = logging.getLogger(__name__)


class CockpitView(QWidget):
    """
    Requirements comparison grid view
    
    Displays master requirements with supplier feedback side-by-side,
    with conflict highlighting and filtering capabilities.
    """
    
    def __init__(self):
        super().__init__()
        self.project_id: Optional[int] = None
        self.requirements: List[MasterRequirement] = []
        self.suppliers = []
        
        self._create_widgets()
        self._connect_signals()
    
    def _create_widgets(self):
        """Create view widgets"""
        layout = QVBoxLayout(self)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search requirements...")
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All")
        self.status_filter.addItem("Accepted")
        self.status_filter.addItem("Clarification Needed")
        self.status_filter.addItem("Rejected")
        filter_layout.addWidget(self.status_filter)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        filter_layout.addWidget(refresh_button)
        
        layout.addLayout(filter_layout)
        
        # Requirements table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(self.table)
    
    def _connect_signals(self):
        """Connect signals"""
        self.search_input.textChanged.connect(self._on_search_changed)
        self.status_filter.currentTextChanged.connect(self._on_filter_changed)
    
    def set_project(self, project_id: int):
        """Set current project"""
        self.project_id = project_id
        self.refresh()
    
    def refresh(self):
        """Refresh the view"""
        if not self.project_id:
            return
        
        self._load_data()
        self._populate_table()
    
    def _load_data(self):
        """Load requirements and suppliers from database"""
        session = db_manager.get_session()
        if not session:
            return
        
        try:
            # Load requirements
            self.requirements = session.query(MasterRequirement).filter(
                MasterRequirement.project_id == self.project_id
            ).all()
            
            # Load suppliers
            self.suppliers = session.query(Supplier).filter(
                Supplier.project_id == self.project_id
            ).all()
        
        finally:
            session.close()
    
    def _populate_table(self):
        """Populate table with requirements and feedback"""
        # Clear table
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        if not self.requirements:
            return

        # Setup columns: ReqIF ID, Master Text, then supplier feedback
        columns = ['ReqIF ID', 'Master Text']
        columns.extend([s.name for s in self.suppliers])

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Load all feedback data in a single batch query
        feedback_lookup = self._load_feedback_data()

        # Get conflicts for this project
        conflicts = {}
        if self.project_id is not None:
            conflicts = conflict_detector.detect_all_conflicts(self.project_id)
        conflict_req_ids = set(conflicts.keys())

        # Populate rows
        for row_idx, req in enumerate(self.requirements):
            self.table.insertRow(row_idx)

            # Check if this requirement has conflicts
            has_conflict = req.id in conflict_req_ids

            # ReqIF ID
            id_item = QTableWidgetItem(req.reqif_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_conflict:
                id_item.setBackground(QColor(CONFLICT_COLOR))
            self.table.setItem(row_idx, 0, id_item)

            # Master Text
            text_item = QTableWidgetItem(req.text_content or '')
            text_item.setFlags(text_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_conflict:
                text_item.setBackground(QColor(CONFLICT_COLOR))
            self.table.setItem(row_idx, 1, text_item)

            # Supplier feedback - use pre-loaded data
            for col_idx, supplier in enumerate(self.suppliers, start=2):
                feedback_key = (req.id, supplier.id)
                feedback = feedback_lookup.get(feedback_key)

                if feedback:
                    status_text = feedback.supplier_status_normalized or 'Not Set'
                    item = QTableWidgetItem(status_text)

                    # Color code by status
                    if feedback.supplier_status_normalized in STATUS_COLORS:
                        color = STATUS_COLORS[feedback.supplier_status_normalized]
                        item.setBackground(QColor(color))
                    # Apply conflict highlighting on top of status colors
                    if has_conflict:
                        item.setBackground(QColor(CONFLICT_COLOR))
                else:
                    item = QTableWidgetItem('')
                    if has_conflict:
                        item.setBackground(QColor(CONFLICT_COLOR))

                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        # Configure frozen columns (first FROZEN_COLUMNS_COUNT columns)
        header = self.table.horizontalHeader()
        for i in range(min(FROZEN_COLUMNS_COUNT, len(columns))):
            # Frozen columns: fixed width, don't stretch
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            # Set reasonable widths for frozen columns
            if i == 0:  # ReqIF ID
                self.table.setColumnWidth(i, 120)
            elif i == 1:  # Master Text
                self.table.setColumnWidth(i, 300)

        # Remaining columns: resize to contents
        for i in range(FROZEN_COLUMNS_COUNT, len(columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        # Enable horizontal scroll bar for supplier columns
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def _load_feedback_data(self):
        """Load all feedback data in a single batch query for performance"""
        if not self.project_id or not self.suppliers:
            return {}

        session = db_manager.get_session()
        if not session:
            return {}

        try:
            # Get all requirement IDs for current project
            req_ids = [req.id for req in self.requirements]
            supplier_ids = [s.id for s in self.suppliers]

            # Batch load all feedback in one query
            feedback_list = session.query(SupplierFeedback).filter(
                SupplierFeedback.master_req_id.in_(req_ids),
                SupplierFeedback.supplier_id.in_(supplier_ids)
            ).all()

            # Create lookup dictionary: (requirement_id, supplier_id) -> feedback
            feedback_lookup = {}
            for feedback in feedback_list:
                key = (feedback.master_req_id, feedback.supplier_id)
                feedback_lookup[key] = feedback

            return feedback_lookup

        finally:
            session.close()
    
    def _on_search_changed(self, text: str):
        """Handle search text changed"""
        self._apply_filters()
    
    def _on_filter_changed(self, status: str):
        """Handle status filter changed"""
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply search and filter to table"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.table.rowCount()):
            # Check search text
            show_row = False
            
            if not search_text:
                show_row = True
            else:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        show_row = True
                        break
            
            # Check status filter
            if show_row and status_filter != 'All':
                show_row = False
                for col in range(2, self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and item.text() == status_filter:
                        show_row = True
                        break
            
            self.table.setRowHidden(row, not show_row)

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
from models.requirement import MasterRequirement, SupplierFeedback
from config import STATUS_COLORS, NormalizedStatus, FROZEN_COLUMNS_COUNT

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
            from models.project import Supplier
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
        
        # Populate rows
        for row_idx, req in enumerate(self.requirements):
            self.table.insertRow(row_idx)
            
            # ReqIF ID
            id_item = QTableWidgetItem(req.reqif_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 0, id_item)
            
            # Master Text
            text_item = QTableWidgetItem(req.master_text or '')
            text_item.setFlags(text_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 1, text_item)
            
            # Supplier feedback
            session = db_manager.get_session()
            if session:
                try:
                    for col_idx, supplier in enumerate(self.suppliers, start=2):
                        feedback = session.query(SupplierFeedback).filter(
                            SupplierFeedback.requirement_id == req.id,
                            SupplierFeedback.supplier_id == supplier.id
                        ).order_by(
                            SupplierFeedback.created_at.desc()
                        ).first()
                        
                        if feedback:
                            status_text = feedback.normalized_status or 'Not Set'
                            item = QTableWidgetItem(status_text)
                            
                            # Color code by status
                            if feedback.normalized_status in STATUS_COLORS:
                                color = STATUS_COLORS[feedback.normalized_status]
                                item.setBackground(QColor(color))
                        else:
                            item = QTableWidgetItem('')
                        
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.table.setItem(row_idx, col_idx, item)
                
                finally:
                    session.close()
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in range(2, len(columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
    
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

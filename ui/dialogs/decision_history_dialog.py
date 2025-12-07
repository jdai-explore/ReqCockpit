"""
Dialog for viewing decision history
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PyQt6.QtCore import Qt

from models.base import db_manager
from models.requirement import CustREDecision
from utils.formatters import format_datetime


class DecisionHistoryDialog(QDialog):
    """Dialog for viewing decision history"""
    
    def __init__(self, parent=None, requirement_id: int = None):
        super().__init__(parent)
        self.requirement_id = requirement_id
        
        self.setWindowTitle("Decision History")
        self.setMinimumSize(600, 400)
        
        self._create_widgets()
        
        if requirement_id:
            self._load_history()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Decision History:"))
        
        # History table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            'Date', 'Status', 'Action Note', 'User'
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
    
    def _load_history(self):
        """Load decision history from database"""
        if not self.requirement_id:
            return
        
        session = db_manager.get_session()
        if not session:
            return
        
        try:
            decisions = session.query(CustREDecision).filter(
                CustREDecision.requirement_id == self.requirement_id
            ).order_by(
                CustREDecision.created_at.desc()
            ).all()
            
            self.table.setRowCount(len(decisions))
            
            for row_idx, decision in enumerate(decisions):
                # Date
                date_item = QTableWidgetItem(
                    format_datetime(decision.created_at)
                )
                date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 0, date_item)
                
                # Status
                status_item = QTableWidgetItem(decision.status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 1, status_item)
                
                # Action Note
                note_item = QTableWidgetItem(decision.action_note or '')
                note_item.setFlags(note_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 2, note_item)
                
                # User (placeholder)
                user_item = QTableWidgetItem("System")
                user_item.setFlags(user_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 3, user_item)
        
        finally:
            session.close()

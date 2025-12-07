"""
Decision panel for CustRE decision making
"""
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTextEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from models.base import db_manager
from models.requirement import MasterRequirement, CustREDecision
from config import DecisionStatus

logger = logging.getLogger(__name__)


class DecisionPanel(QWidget):
    """
    Panel for making CustRE decisions on requirements
    
    Allows selection of decision status and action notes.
    """
    
    decision_made = pyqtSignal(int, str, str)  # requirement_id, status, note
    
    def __init__(self):
        super().__init__()
        self.current_requirement_id: Optional[int] = None
        self.project_id: Optional[int] = None
        
        self._create_widgets()
        self._connect_signals()
    
    def _create_widgets(self):
        """Create panel widgets"""
        layout = QVBoxLayout(self)
        
        # Decision group
        decision_group = QGroupBox("Decision")
        decision_layout = QVBoxLayout(decision_group)
        
        # Status selection
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        
        self.status_combo = QComboBox()
        for status in DecisionStatus:
            self.status_combo.addItem(status.value, status.value)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        
        decision_layout.addLayout(status_layout)
        
        # Action note
        note_layout = QVBoxLayout()
        note_layout.addWidget(QLabel("Action Note:"))
        
        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(100)
        self.note_input.setPlaceholderText("Enter decision rationale or action items...")
        note_layout.addWidget(self.note_input)
        
        decision_layout.addLayout(note_layout)
        
        layout.addWidget(decision_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Decision")
        self.save_button.clicked.connect(self._save_decision)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_form)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect signals"""
        pass
    
    def set_requirement(self, requirement_id: int, project_id: int):
        """Set current requirement for decision"""
        self.current_requirement_id = requirement_id
        self.project_id = project_id
        
        # Load existing decision if any
        self._load_existing_decision()
    
    def _load_existing_decision(self):
        """Load existing decision for current requirement"""
        if not self.current_requirement_id:
            self._clear_form()
            return
        
        session = db_manager.get_session()
        if not session:
            return
        
        try:
            decision = session.query(CustREDecision).filter(
                CustREDecision.requirement_id == self.current_requirement_id
            ).order_by(
                CustREDecision.created_at.desc()
            ).first()
            
            if decision:
                # Set status
                index = self.status_combo.findData(decision.status)
                if index >= 0:
                    self.status_combo.setCurrentIndex(index)
                
                # Set note
                self.note_input.setPlainText(decision.action_note or '')
            else:
                self._clear_form()
        
        finally:
            session.close()
    
    def _save_decision(self):
        """Save decision to database"""
        if not self.current_requirement_id or not self.project_id:
            QMessageBox.warning(self, "Warning", "No requirement selected")
            return
        
        status = self.status_combo.currentData()
        note = self.note_input.toPlainText().strip()
        
        session = db_manager.get_session()
        if not session:
            QMessageBox.critical(self, "Error", "No database connection")
            return
        
        try:
            # Check if decision already exists
            existing_decision = session.query(CustREDecision).filter(
                CustREDecision.requirement_id == self.current_requirement_id
            ).first()
            
            if existing_decision:
                # Update existing
                existing_decision.status = status
                existing_decision.action_note = note
            else:
                # Create new
                decision = CustREDecision(
                    requirement_id=self.current_requirement_id,
                    project_id=self.project_id,
                    status=status,
                    action_note=note
                )
                session.add(decision)
            
            session.commit()
            
            QMessageBox.information(self, "Success", "Decision saved")
            self.decision_made.emit(self.current_requirement_id, status, note)
        
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save decision: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save decision: {str(e)}")
        
        finally:
            session.close()
    
    def _clear_form(self):
        """Clear form fields"""
        self.status_combo.setCurrentIndex(0)
        self.note_input.clear()

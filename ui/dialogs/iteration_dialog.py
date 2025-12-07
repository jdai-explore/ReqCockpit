"""
Dialog for creating and managing iterations
"""
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QMessageBox
)

from utils.validators import validate_iteration_id


class IterationDialog(QDialog):
    """Dialog for creating/editing iterations"""
    
    def __init__(self, parent=None, mode: str = 'create'):
        super().__init__(parent)
        self.mode = mode
        self.iteration_data = {}
        
        self.setWindowTitle("New Iteration" if mode == 'create' else "Edit Iteration")
        self.setMinimumWidth(400)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        layout = QVBoxLayout(self)
        
        # Iteration ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Iteration ID:"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g., I-001_Round1")
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)
        
        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        desc_layout.addWidget(self.description_input)
        layout.addLayout(desc_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _on_ok(self):
        """Handle OK button"""
        iteration_id = self.id_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        # Validate
        is_valid, error_msg = validate_iteration_id(iteration_id)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        self.iteration_data = {
            'id': iteration_id,
            'description': description
        }
        
        self.accept()
    
    def get_iteration_data(self) -> Dict[str, Any]:
        """Get iteration data from dialog"""
        return self.iteration_data

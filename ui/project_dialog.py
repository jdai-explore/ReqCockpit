"""
Project creation and management dialogs
"""
from typing import Dict, Any, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

from utils.validators import validate_project_name


class ProjectDialog(QDialog):
    """Dialog for creating or editing projects"""
    
    def __init__(self, parent=None, mode: str = 'create'):
        super().__init__(parent)
        self.mode = mode
        self.project_data = {}
        
        self.setWindowTitle("New Project" if mode == 'create' else "Edit Project")
        self.setMinimumWidth(500)
        
        self._create_widgets()
        self._connect_signals()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        layout = QVBoxLayout(self)
        
        # Project name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        desc_layout.addWidget(self.description_input)
        layout.addLayout(desc_layout)
        
        # Directory selection
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Location:"))
        self.directory_input = QLineEdit()
        self.directory_input.setText(str(Path.home()))
        dir_layout.addWidget(self.directory_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_button)
        layout.addLayout(dir_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals"""
        pass
    
    def _browse_directory(self):
        """Browse for directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Location",
            str(Path.home())
        )
        
        if directory:
            self.directory_input.setText(directory)
    
    def _on_ok(self):
        """Handle OK button"""
        name = self.name_input.text().strip()
        directory = self.directory_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        # Validate
        is_valid, error_msg = validate_project_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        if not directory:
            QMessageBox.warning(self, "Validation Error", "Please select a location")
            return
        
        # Check if directory exists
        if not Path(directory).exists():
            QMessageBox.warning(self, "Validation Error", "Directory does not exist")
            return
        
        self.project_data = {
            'name': name,
            'directory': directory,
            'description': description
        }
        
        self.accept()
    
    def get_project_data(self) -> Dict[str, Any]:
        """Get project data from dialog"""
        return self.project_data

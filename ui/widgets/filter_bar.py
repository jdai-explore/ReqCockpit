"""
Filter toolbar widget
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QComboBox, QLabel, QPushButton
)
from PyQt6.QtCore import pyqtSignal


class FilterBar(QWidget):
    """
    Toolbar for filtering requirements
    """
    
    search_changed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    supplier_changed = pyqtSignal(int)
    refresh_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._create_widgets()
        self._connect_signals()
    
    def _create_widgets(self):
        """Create filter widgets"""
        layout = QHBoxLayout(self)
        
        # Search box
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search requirements...")
        self.search_input.setMaximumWidth(250)
        layout.addWidget(self.search_input)
        
        # Status filter
        layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("All")
        self.status_combo.addItem("Accepted")
        self.status_combo.addItem("Clarification Needed")
        self.status_combo.addItem("Rejected")
        self.status_combo.setMaximumWidth(200)
        layout.addWidget(self.status_combo)
        
        # Supplier filter
        layout.addWidget(QLabel("Supplier:"))
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("All", -1)
        self.supplier_combo.setMaximumWidth(200)
        layout.addWidget(self.supplier_combo)
        
        layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        layout.addWidget(self.refresh_button)
    
    def _connect_signals(self):
        """Connect signals"""
        self.search_input.textChanged.connect(self.search_changed.emit)
        self.status_combo.currentTextChanged.connect(self.status_changed.emit)
        self.supplier_combo.currentDataChanged.connect(self.supplier_changed.emit)
        self.refresh_button.clicked.connect(self.refresh_clicked.emit)
    
    def add_supplier(self, supplier_id: int, supplier_name: str):
        """Add supplier to filter dropdown"""
        self.supplier_combo.addItem(supplier_name, supplier_id)
    
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_input.text()
    
    def get_status_filter(self) -> str:
        """Get current status filter"""
        return self.status_combo.currentText()
    
    def get_supplier_filter(self) -> int:
        """Get current supplier filter"""
        return self.supplier_combo.currentData()

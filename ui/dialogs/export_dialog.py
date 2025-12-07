"""
Dialog for configuring export options
"""
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QListWidget, QListWidgetItem, QPushButton,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt

from models.base import db_manager
from models.project import Supplier
from services.export_service import export_service


class ExportDialog(QDialog):
    """Dialog for configuring export options"""
    
    def __init__(self, parent=None, project_id: int = None):
        super().__init__(parent)
        self.project_id = project_id
        self.suppliers = []
        
        self.setWindowTitle("Export Project")
        self.setMinimumWidth(500)
        
        self._create_widgets()
        
        if project_id:
            self._load_suppliers()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        layout = QVBoxLayout(self)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("Excel (.xlsx)")
        self.format_combo.addItem("CSV (.csv)")
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        
        layout.addLayout(format_layout)
        
        # Options
        self.include_decisions_check = QCheckBox("Include Decisions")
        self.include_decisions_check.setChecked(True)
        layout.addWidget(self.include_decisions_check)
        
        # Supplier selection
        layout.addWidget(QLabel("Suppliers to Include:"))
        
        self.supplier_list = QListWidget()
        self.supplier_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.supplier_list)
        
        # Select all / Deselect all
        select_layout = QHBoxLayout()
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self._select_all_suppliers)
        select_layout.addWidget(select_all_button)
        
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self._deselect_all_suppliers)
        select_layout.addWidget(deselect_all_button)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("Export")
        export_button.clicked.connect(self._on_export)
        button_layout.addWidget(export_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _load_suppliers(self):
        """Load suppliers from database"""
        session = db_manager.get_session()
        if not session:
            return
        
        try:
            self.suppliers = session.query(Supplier).filter(
                Supplier.project_id == self.project_id
            ).all()
            
            for supplier in self.suppliers:
                item = QListWidgetItem(supplier.name)
                item.setData(Qt.ItemDataRole.UserRole, supplier.id)
                item.setCheckState(Qt.CheckState.Checked)
                self.supplier_list.addItem(item)
        
        finally:
            session.close()
    
    def _select_all_suppliers(self):
        """Select all suppliers"""
        for i in range(self.supplier_list.count()):
            item = self.supplier_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def _deselect_all_suppliers(self):
        """Deselect all suppliers"""
        for i in range(self.supplier_list.count()):
            item = self.supplier_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def _on_export(self):
        """Handle export button"""
        # Get selected suppliers
        selected_suppliers = []
        for i in range(self.supplier_list.count()):
            item = self.supplier_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_suppliers.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not selected_suppliers:
            QMessageBox.warning(self, "Warning", "Please select at least one supplier")
            return
        
        # Get export format
        is_xlsx = self.format_combo.currentIndex() == 0
        file_filter = "Excel Files (*.xlsx)" if is_xlsx else "CSV Files (*.csv)"
        default_suffix = ".xlsx" if is_xlsx else ".csv"
        
        # Ask for file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Project",
            f"export{default_suffix}",
            file_filter
        )
        
        if not file_path:
            return
        
        # Perform export
        include_decisions = self.include_decisions_check.isChecked()
        
        if is_xlsx:
            result = export_service.export_to_xlsx(
                self.project_id,
                file_path,
                include_decisions=include_decisions,
                selected_suppliers=selected_suppliers
            )
        else:
            result = export_service.export_to_csv(
                self.project_id,
                file_path,
                include_decisions=include_decisions,
                selected_suppliers=selected_suppliers
            )
        
        if result['success']:
            QMessageBox.information(
                self,
                "Success",
                f"Exported {result['rows_exported']} rows to {file_path}"
            )
            self.accept()
        else:
            QMessageBox.critical(self, "Export Error", result['message'])

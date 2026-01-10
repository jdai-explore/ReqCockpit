"""
Import wizard for ReqIF files
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QProgressBar, QMessageBox,
    QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from services.database_service import DatabaseService
from services.import_service import ImportService


class ImportWorker(QThread):
    """Worker thread for import operations"""

    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)

    def __init__(self, import_type: str, file_path: str, project_id: int = None, supplier_name: str = None):
        super().__init__()
        self.import_type = import_type
        self.file_path = file_path
        self.project_id = project_id
        self.supplier_name = supplier_name
        self.import_service = ImportService()
    
    def run(self):
        """Run import in background thread"""
        try:
            if self.import_type == 'master':
                result = self.import_service.import_master_specification(
                    self.file_path,
                    progress_callback=self.progress.emit
                )
            else:  # supplier
                # For now, use a default iteration - this should be improved
                # to let user select iteration
                if not self.supplier_name:
                    result = {
                        'success': False,
                        'message': 'No supplier selected',
                        'imported_count': 0
                    }
                else:
                    iteration_id = 1  # TODO: Get from UI or create new iteration
                    result = self.import_service.import_supplier_feedback(
                        self.file_path,
                        self.supplier_name,
                        iteration_id,
                        progress_callback=self.progress.emit
                    )

            self.finished.emit(result)
        
        except Exception as e:
            self.finished.emit({
                'success': False,
                'message': str(e),
                'imported_count': 0
            })


class ImportWizard(QDialog):
    """Wizard for importing ReqIF files"""
    
    def __init__(self, parent=None, import_type: str = 'master', project_id: int = None):
        super().__init__(parent)
        self.import_type = import_type
        self.project_id = project_id
        self.import_worker = None
        
        title = "Import Master Specification" if import_type == 'master' else "Import Supplier Response"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        self._create_widgets()
        self._connect_signals()
    
    def _create_widgets(self):
        """Create wizard widgets"""
        layout = QVBoxLayout(self)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("ReqIF File:"))
        
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        file_layout.addWidget(self.file_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_button)
        
        layout.addLayout(file_layout)
        
        # Supplier selection (for supplier import)
        if self.import_type == 'supplier':
            supplier_layout = QHBoxLayout()
            supplier_layout.addWidget(QLabel("Supplier:"))

            self.supplier_combo = QComboBox()
            self._load_suppliers()
            supplier_layout.addWidget(self.supplier_combo)

            layout.addLayout(supplier_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self._start_import)
        button_layout.addWidget(self.import_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals"""
        pass

    def _load_suppliers(self):
        """Load suppliers from database for supplier selection"""
        if self.import_type != 'supplier':
            return

        try:
            suppliers = DatabaseService.list_suppliers()

            if suppliers:
                self.supplier_combo.clear()
                for supplier in suppliers:
                    self.supplier_combo.addItem(supplier['name'], supplier['id'])

                # Select first supplier by default
                if self.supplier_combo.count() > 0:
                    self.supplier_combo.setCurrentIndex(0)
            else:
                # No suppliers found - add a placeholder
                self.supplier_combo.clear()
                self.supplier_combo.addItem("No suppliers available", -1)
                self.supplier_combo.setEnabled(False)

        except Exception as e:
            # Handle database errors gracefully
            self.supplier_combo.clear()
            self.supplier_combo.addItem(f"Error loading suppliers: {str(e)}", -1)
            self.supplier_combo.setEnabled(False)
    
    def _browse_file(self):
        """Browse for ReqIF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ReqIF File",
            "",
            "ReqIF Files (*.reqif);;All Files (*)"
        )
        
        if file_path:
            self.file_input.setText(file_path)
    
    def _start_import(self):
        """Start import process"""
        file_path = self.file_input.text().strip()

        if not file_path:
            QMessageBox.warning(self, "Validation Error", "Please select a file")
            return

        # For supplier import, validate supplier selection
        if self.import_type == 'supplier':
            if not hasattr(self, 'supplier_combo') or self.supplier_combo.currentData() == -1:
                QMessageBox.warning(self, "Validation Error", "Please select a valid supplier")
                return

        # Disable import button and show progress
        self.import_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)

        # Get supplier name for supplier imports
        supplier_name = None
        if self.import_type == 'supplier':
            supplier_name = self.supplier_combo.currentText()

        # Create and start worker thread
        self.import_worker = ImportWorker(
            self.import_type,
            file_path,
            self.project_id,
            supplier_name
        )
        self.import_worker.progress.connect(self._on_progress)
        self.import_worker.finished.connect(self._on_import_finished)
        self.import_worker.start()
    
    def _on_progress(self, current: int, total: int, message: str):
        """Handle progress update"""
        if total > 0:
            self.progress_bar.setValue(int(current / total * 100))
        self.progress_label.setText(message)
    
    def _on_import_finished(self, result: dict):
        """Handle import finished"""
        self.import_button.setEnabled(True)
        
        if result['success']:
            QMessageBox.information(
                self,
                "Success",
                f"Import completed: {result['imported_count']} items imported"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Import Error",
                result['message']
            )

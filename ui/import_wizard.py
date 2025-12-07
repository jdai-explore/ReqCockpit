"""
Import wizard for ReqIF files
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QProgressBar, QMessageBox,
    QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from services.import_service import ImportService


class ImportWorker(QThread):
    """Worker thread for import operations"""
    
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)
    
    def __init__(self, import_type: str, file_path: str, project_id: int = None):
        super().__init__()
        self.import_type = import_type
        self.file_path = file_path
        self.project_id = project_id
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
                result = self.import_service.import_supplier_feedback(
                    self.file_path,
                    self.project_id,
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
            # TODO: Load suppliers from database
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
        
        # Disable import button and show progress
        self.import_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create and start worker thread
        self.import_worker = ImportWorker(
            self.import_type,
            file_path,
            self.project_id
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

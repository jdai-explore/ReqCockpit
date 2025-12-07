"""
Main application window for ReqCockpit
"""
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QMessageBox,
    QFileDialog, QTabWidget
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from config import APP_NAME, APP_VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from models.base import db_manager
from models.project import Project
from services.database_service import DatabaseService
from services.import_service import ImportService
from services.export_service import export_service
from .cockpit_view import CockpitView
from .dashboard_view import DashboardView
from .project_dialog import ProjectDialog

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window for ReqCockpit
    
    Provides menu bar, toolbars, and central widget for displaying
    project data and analytics.
    """
    
    # Signals
    project_opened = pyqtSignal(int)  # project_id
    project_closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        self.current_project_id: Optional[int] = None
        self.import_service = ImportService()
        
        # Create UI
        self._create_menu_bar()
        self._create_toolbars()
        self._create_central_widget()
        self._create_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Load recent projects or show welcome
        self._load_recent_projects()
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_project_action = QAction("&New Project", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("&Open Project", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        import_master_action = QAction("Import &Master Specification", self)
        import_master_action.setShortcut("Ctrl+I")
        import_master_action.triggered.connect(self._import_master)
        file_menu.addAction(import_master_action)
        
        import_supplier_action = QAction("Import &Supplier Response", self)
        import_supplier_action.setShortcut("Ctrl+Shift+I")
        import_supplier_action.triggered.connect(self._import_supplier)
        file_menu.addAction(import_supplier_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_view)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbars(self):
        """Create application toolbars"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setObjectName("MainToolbar")
        toolbar.setIconSize(QSize(24, 24))
        
        # Add toolbar actions
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self._new_project)
        toolbar.addAction(new_project_action)
        
        open_project_action = QAction("Open Project", self)
        open_project_action.triggered.connect(self._open_project)
        toolbar.addAction(open_project_action)
        
        toolbar.addSeparator()
        
        import_action = QAction("Import", self)
        import_action.triggered.connect(self._import_master)
        toolbar.addAction(import_action)
        
        export_action = QAction("Export", self)
        export_action.triggered.connect(self._export_data)
        toolbar.addAction(export_action)
    
    def _create_central_widget(self):
        """Create central widget with tabs"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Cockpit view (requirements comparison)
        self.cockpit_view = CockpitView()
        self.tabs.addTab(self.cockpit_view, "Cockpit")
        
        # Dashboard view (analytics)
        self.dashboard_view = DashboardView()
        self.tabs.addTab(self.dashboard_view, "Dashboard")
        
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect internal signals"""
        self.project_opened.connect(self._on_project_opened)
        self.project_closed.connect(self._on_project_closed)
    
    def _new_project(self):
        """Create new project"""
        dialog = ProjectDialog(self, mode='create')
        if dialog.exec():
            project_data = dialog.get_project_data()
            result = DatabaseService.create_project(
                name=project_data['name'],
                directory=project_data['directory'],
                description=project_data.get('description')
            )
            
            if result['success']:
                self.status_bar.showMessage(f"Project created: {project_data['name']}")
                # Open the new project
                self._open_project_by_path(result['project']['db_path'])
            else:
                QMessageBox.critical(self, "Error", result['message'])
    
    def _open_project(self):
        """Open existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "ReqCockpit Projects (*.sqlite);;All Files (*)"
        )
        
        if file_path:
            self._open_project_by_path(file_path)
    
    def _open_project_by_path(self, file_path: str):
        """Open project by file path"""
        try:
            # Connect to database
            if not db_manager.connect(file_path):
                QMessageBox.critical(self, "Error", "Failed to connect to database")
                return
            
            # Get project from database
            session = db_manager.get_session()
            if session:
                project = session.query(Project).first()
                session.close()
                
                if project:
                    self.current_project_id = project.id
                    self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {project.name}")
                    self.status_bar.showMessage(f"Opened: {project.name}")
                    
                    # Update views
                    self.cockpit_view.set_project(project.id)
                    self.dashboard_view.set_project(project.id)
                    
                    self.project_opened.emit(project.id)
                else:
                    QMessageBox.warning(self, "Warning", "No project found in database")
            else:
                QMessageBox.critical(self, "Error", "Failed to connect to database")
        
        except Exception as e:
            logger.error(f"Failed to open project: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open project: {str(e)}")
    
    def _import_master(self):
        """Import master specification"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Warning", "Please open a project first")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Master Specification",
            "",
            "ReqIF Files (*.reqif);;All Files (*)"
        )
        
        if file_path:
            self.status_bar.showMessage("Importing master specification...")
            
            def progress_callback(current, total, message):
                self.status_bar.showMessage(f"{message} ({current}/{total})")
            
            result = self.import_service.import_master_specification(
                file_path,
                progress_callback=progress_callback
            )
            
            if result['success']:
                self.status_bar.showMessage(
                    f"Imported {result['imported_count']} requirements"
                )
                self.cockpit_view.refresh()
                self.dashboard_view.refresh()
            else:
                QMessageBox.critical(self, "Import Error", result['message'])
    
    def _import_supplier(self):
        """Import supplier response"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Warning", "Please open a project first")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Supplier Response",
            "",
            "ReqIF Files (*.reqif);;All Files (*)"
        )
        
        if file_path:
            self.status_bar.showMessage("Importing supplier response...")
            
            def progress_callback(current, total, message):
                self.status_bar.showMessage(f"{message} ({current}/{total})")
            
            result = self.import_service.import_supplier_feedback(
                file_path,
                self.current_project_id,
                progress_callback=progress_callback
            )
            
            if result['success']:
                self.status_bar.showMessage(
                    f"Imported {result['imported_count']} feedback entries"
                )
                self.cockpit_view.refresh()
                self.dashboard_view.refresh()
            else:
                QMessageBox.critical(self, "Import Error", result['message'])
    
    def _export_data(self):
        """Export project data"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Warning", "Please open a project first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Project",
            "",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if file_path:
            self.status_bar.showMessage("Exporting data...")
            
            if file_path.endswith('.xlsx'):
                result = export_service.export_to_xlsx(
                    self.current_project_id,
                    file_path
                )
            else:
                result = export_service.export_to_csv(
                    self.current_project_id,
                    file_path
                )
            
            if result['success']:
                self.status_bar.showMessage(f"Exported {result['rows_exported']} rows")
                QMessageBox.information(self, "Success", result['message'])
            else:
                QMessageBox.critical(self, "Export Error", result['message'])
    
    def _refresh_view(self):
        """Refresh current view"""
        if self.current_project_id:
            self.cockpit_view.refresh()
            self.dashboard_view.refresh()
            self.status_bar.showMessage("View refreshed")
    
    def _on_project_opened(self, project_id: int):
        """Handle project opened signal"""
        logger.info(f"Project opened: {project_id}")
    
    def _on_project_closed(self):
        """Handle project closed signal"""
        self.current_project_id = None
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.status_bar.showMessage("No project open")
    
    def _load_recent_projects(self):
        """Load recent projects on startup"""
        # TODO: Implement recent projects loading
        pass
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Multi-Partner Requirements Aggregation Tool\n\n"
            "© 2025 Automotive Systems"
        )

"""
Main application window for ReqCockpit
"""
import logging
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QMessageBox,
    QFileDialog, QTabWidget
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from config import APP_NAME, APP_VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, RECENT_PROJECTS_FILE, MAX_RECENT_PROJECTS
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
        self.recent_projects = []

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

        # Recent projects submenu
        self._create_recent_projects_menu(file_menu)
        
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

                    # Add to recent projects
                    self._add_to_recent_projects(file_path, project.name)

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
    
    def _create_recent_projects_menu(self, file_menu: QMenu):
        """Create recent projects submenu"""
        self.recent_menu = file_menu.addMenu("Recent &Projects")
        self.recent_menu.setEnabled(False)  # Initially disabled until projects are loaded
        self._update_recent_projects_menu()

    def _load_recent_projects(self):
        """Load recent projects from file on startup"""
        try:
            if RECENT_PROJECTS_FILE.exists():
                with open(RECENT_PROJECTS_FILE, 'r', encoding='utf-8') as f:
                    self.recent_projects = json.load(f)
                self._update_recent_projects_menu()
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # If file doesn't exist or is corrupted, start with empty list
            self.recent_projects = []
            logger.warning("Could not load recent projects file, starting with empty list")

    def _save_recent_projects(self):
        """Save recent projects to file"""
        try:
            RECENT_PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(RECENT_PROJECTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.recent_projects, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save recent projects: {e}")

    def _add_to_recent_projects(self, project_path: str, project_name: str):
        """Add a project to the recent projects list"""
        # Remove if already exists
        self.recent_projects = [
            p for p in self.recent_projects
            if p.get('path') != project_path
        ]

        # Add to beginning of list
        self.recent_projects.insert(0, {
            'name': project_name,
            'path': project_path,
            'last_opened': self._get_current_timestamp()
        })

        # Keep only the most recent projects
        self.recent_projects = self.recent_projects[:MAX_RECENT_PROJECTS]

        # Save to file
        self._save_recent_projects()

        # Update menu
        self._update_recent_projects_menu()

    def _update_recent_projects_menu(self):
        """Update the recent projects menu with current list"""
        self.recent_menu.clear()

        if not self.recent_projects:
            no_recent_action = QAction("No recent projects", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
            self.recent_menu.setEnabled(False)
            return

        self.recent_menu.setEnabled(True)

        for i, project in enumerate(self.recent_projects):
            # Create action with project name and path
            action_text = f"{i+1}. {project['name']}"
            action = QAction(action_text, self)
            action.setData(project['path'])
            action.triggered.connect(lambda checked, path=project['path']: self._open_recent_project(path))
            self.recent_menu.addAction(action)

        # Add clear recent projects option
        self.recent_menu.addSeparator()
        clear_action = QAction("Clear Recent Projects", self)
        clear_action.triggered.connect(self._clear_recent_projects)
        self.recent_menu.addAction(clear_action)

    def _open_recent_project(self, project_path: str):
        """Open a project from the recent projects list"""
        if Path(project_path).exists():
            self._open_project_by_path(project_path)
        else:
            # Remove from list if file no longer exists
            QMessageBox.warning(
                self,
                "Project Not Found",
                f"The project file '{project_path}' could not be found.\n"
                "It will be removed from the recent projects list."
            )
            self.recent_projects = [
                p for p in self.recent_projects
                if p.get('path') != project_path
            ]
            self._save_recent_projects()
            self._update_recent_projects_menu()

    def _clear_recent_projects(self):
        """Clear all recent projects"""
        reply = QMessageBox.question(
            self,
            "Clear Recent Projects",
            "Are you sure you want to clear the recent projects list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.recent_projects = []
            self._save_recent_projects()
            self._update_recent_projects_menu()

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Multi-Partner Requirements Aggregation Tool\n\n"
            "© 2025 Automotive Systems"
        )

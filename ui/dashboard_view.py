"""
Dashboard view - Analytics and KPI display
"""
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from services.analytics_service import analytics_service

logger = logging.getLogger(__name__)


class DashboardView(QWidget):
    """
    Dashboard view for project analytics and KPIs
    
    Displays project overview, status distribution, supplier performance,
    and decision tracking metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.project_id: Optional[int] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dashboard widgets"""
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for dashboard content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Overview section
        overview_group = QGroupBox("Project Overview")
        overview_layout = QGridLayout(overview_group)
        
        self.overview_labels = {}
        metrics = [
            ('total_requirements', 'Total Requirements'),
            ('total_suppliers', 'Total Suppliers'),
            ('total_iterations', 'Total Iterations'),
            ('total_decisions', 'Total Decisions')
        ]
        
        for idx, (key, label) in enumerate(metrics):
            row = idx // 2
            col = idx % 2
            
            label_widget = QLabel(f"{label}:")
            label_widget.setFont(QFont('Arial', 10, QFont.Weight.Bold))
            overview_layout.addWidget(label_widget, row, col * 2)
            
            value_widget = QLabel("0")
            value_widget.setFont(QFont('Arial', 14, QFont.Weight.Bold))
            overview_layout.addWidget(value_widget, row, col * 2 + 1)
            
            self.overview_labels[key] = value_widget
        
        content_layout.addWidget(overview_group)
        
        # Status distribution section
        status_group = QGroupBox("Status Distribution")
        status_layout = QVBoxLayout(status_group)
        
        self.status_labels = {}
        statuses = ['Accepted', 'Clarification Needed', 'Rejected', 'Not Set']
        
        for status in statuses:
            h_layout = QHBoxLayout()
            
            status_label = QLabel(f"{status}:")
            h_layout.addWidget(status_label)
            
            count_label = QLabel("0")
            count_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
            h_layout.addWidget(count_label)
            
            h_layout.addStretch()
            status_layout.addLayout(h_layout)
            
            self.status_labels[status] = count_label
        
        content_layout.addWidget(status_group)
        
        # Supplier performance section
        supplier_group = QGroupBox("Supplier Performance")
        supplier_layout = QVBoxLayout(supplier_group)
        
        self.supplier_labels = {}
        
        content_layout.addWidget(supplier_group)
        
        # Decision summary section
        decision_group = QGroupBox("Decision Summary")
        decision_layout = QVBoxLayout(decision_group)
        
        self.decision_labels = {}
        decision_statuses = ['Accepted', 'Rejected', 'Modified', 'Deferred']
        
        for status in decision_statuses:
            h_layout = QHBoxLayout()
            
            status_label = QLabel(f"{status}:")
            h_layout.addWidget(status_label)
            
            count_label = QLabel("0")
            count_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
            h_layout.addWidget(count_label)
            
            h_layout.addStretch()
            decision_layout.addLayout(h_layout)
            
            self.decision_labels[status] = count_label
        
        content_layout.addWidget(decision_group)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def set_project(self, project_id: int):
        """Set current project"""
        self.project_id = project_id
        self.refresh()
    
    def refresh(self):
        """Refresh dashboard data"""
        if not self.project_id:
            return
        
        try:
            # Get dashboard data
            dashboard_data = analytics_service.get_dashboard_data(self.project_id)
            
            # Update overview
            overview = dashboard_data.get('overview', {})
            for key, label_widget in self.overview_labels.items():
                value = overview.get(key, 0)
                label_widget.setText(str(value))
            
            # Update status distribution
            status_dist = dashboard_data.get('status_distribution', {})
            for status, label_widget in self.status_labels.items():
                # Map display names to normalized status values
                status_key = status
                if status == 'Clarification Needed':
                    status_key = 'Clarification Needed'
                
                count = status_dist.get(status_key, 0)
                label_widget.setText(str(count))
            
            # Update supplier performance
            suppliers = dashboard_data.get('supplier_performance', [])
            # TODO: Implement supplier performance display
            
            # Update decision summary
            decision_summary = dashboard_data.get('decision_summary', {})
            by_status = decision_summary.get('by_status', {})
            for status, label_widget in self.decision_labels.items():
                count = by_status.get(status, 0)
                label_widget.setText(str(count))
        
        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")

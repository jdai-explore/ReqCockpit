"""
Status badge widget for displaying requirement status
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

from config import STATUS_COLORS
from utils.formatters import format_status_badge


class StatusBadge(QLabel):
    """
    Widget for displaying status as a colored badge
    """
    
    def __init__(self, status: str = None):
        super().__init__()
        self.status = status
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont('Arial', 9, QFont.Weight.Bold))
        self.setMinimumWidth(120)
        self.setMinimumHeight(30)
        
        if status:
            self.set_status(status)
    
    def set_status(self, status: str):
        """Set the status and update appearance"""
        self.status = status
        
        # Set text
        self.setText(format_status_badge(status))
        
        # Set background color
        if status in STATUS_COLORS:
            color = STATUS_COLORS[status]
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                }}
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #6c757d;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                }
            """)

"""
Iteration selector widget
"""
from typing import List, Optional

from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import pyqtSignal

from models.base import db_manager
from models.project import Iteration


class IterationSelector(QComboBox):
    """
    Dropdown for selecting iterations
    """
    
    iteration_selected = pyqtSignal(int)  # iteration_id
    
    def __init__(self):
        super().__init__()
        self.project_id: Optional[int] = None
        
        self.currentIndexChanged.connect(self._on_selection_changed)
    
    def load_iterations(self, project_id: int):
        """Load iterations for a project"""
        self.project_id = project_id
        self.clear()
        
        session = db_manager.get_session()
        if not session:
            return
        
        try:
            iterations = session.query(Iteration).filter(
                Iteration.project_id == project_id
            ).order_by(Iteration.created_at.desc()).all()
            
            for iteration in iterations:
                self.addItem(iteration.name, iteration.id)
        
        finally:
            session.close()
    
    def _on_selection_changed(self, index: int):
        """Handle selection change"""
        if index >= 0:
            iteration_id = self.currentData()
            if iteration_id:
                self.iteration_selected.emit(iteration_id)
    
    def get_selected_iteration_id(self) -> Optional[int]:
        """Get currently selected iteration ID"""
        return self.currentData()

"""
Models package for ReqCockpit

This package contains all SQLAlchemy ORM models for the application.
Models are organized by domain concept for clarity and maintainability.
"""

from .base import Base, DatabaseManager, db_manager
from .project import Project
from .iteration import Iteration
from .supplier import Supplier
from .requirement import MasterRequirement
from .feedback import SupplierFeedback
from .decision import CustREDecision

__all__ = [
    # Base
    'Base',
    'DatabaseManager',
    'db_manager',
    
    # Core entities
    'Project',
    'Iteration',
    'Supplier',
    'MasterRequirement',
    'SupplierFeedback',
    'CustREDecision',
]

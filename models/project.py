"""
Project model for ReqCockpit

This module defines the Project model which serves as the top-level container
for all requirements, suppliers, and iterations in the ReqCockpit system.
"""
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Project(Base):
    """
    Represents a project in ReqCockpit, serving as the top-level container.
    
    A project contains all requirements, suppliers, and iterations for a specific
    Request for Quotation (RFQ) or development effort.
    
    Attributes:
        id: Primary key
        name: Project name (e.g., "2023-11_Steering_Control_Module")
        description: Optional detailed description
        customer: Name of the customer or OEM
        created_at: When the project was created
        updated_at: When the project was last modified
        
    Relationships:
        iterations: All iterations within this project
        suppliers: All suppliers involved in this project
        master_requirements: All requirements in the master specification
    """
    __tablename__ = "projects"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Project identification
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    customer = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    iterations = relationship(
        "Iteration", 
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    suppliers = relationship(
        "Supplier",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    master_requirements = relationship(
        "MasterRequirement",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert project to dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the project
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'customer': self.customer,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'iteration_count': len(self.iterations),
            'supplier_count': len(self.suppliers),
            'requirement_count': len(self.master_requirements)
        }
    
    def get_supplier_by_name(self, name: str):
        """
        Find a supplier by name (case-insensitive).
        
        Args:
            name: Supplier name to search for
            
        Returns:
            Optional[Supplier]: The matching supplier or None
        """
        name_lower = name.lower()
        for supplier in self.suppliers:
            if supplier.name.lower() == name_lower:
                return supplier
        return None
    
    def get_latest_iteration(self):
        """
        Get the most recent iteration by creation date.
        
        Returns:
            Optional[Iteration]: The latest iteration or None if none exist
        """
        if not self.iterations:
            return None
        return max(self.iterations, key=lambda x: x.created_at)
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"

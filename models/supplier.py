"""
Supplier and StatusMapping models for ReqCockpit

This module defines the Supplier and StatusMapping models used to manage
supplier information and status normalization in the requirements management system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class Supplier(Base):
    """
    Represents a supplier in the ReqCockpit system.
    
    Suppliers provide feedback on requirements and are associated with projects.
    Each supplier can have multiple status mappings to normalize their status values.
    """
    __tablename__ = "suppliers"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to project
    project_id = Column(
        Integer, 
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Supplier details
    name = Column(String(200), nullable=False)
    short_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="suppliers")
    status_mappings = relationship(
        "StatusMapping", 
        back_populates="supplier",
        cascade="all, delete-orphan"
    )
    feedback = relationship("SupplierFeedback", back_populates="supplier")
    
    def get_display_name(self) -> str:
        """
        Get the display name for the supplier.
        
        Returns:
            str: The supplier's short name if available, otherwise the full name.
        """
        return self.short_name or self.name
    
    def __repr__(self) -> str:
        return f"<Supplier(id={self.id}, name='{self.name}')>"


class StatusMapping(Base):
    """
    Maps supplier-specific status values to normalized status values.
    
    This allows different suppliers to use their own status terminology while
    maintaining consistent status values in the system.
    """
    __tablename__ = "status_mappings"
    __table_args__ = (
        UniqueConstraint('supplier_id', 'original_status', name='uq_supplier_status'),
    )
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to supplier
    supplier_id = Column(
        Integer, 
        ForeignKey('suppliers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Status mapping
    original_status = Column(String(100), nullable=False)
    normalized_status = Column(String(50), nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="status_mappings")
    
    @classmethod
    def create_default_mappings(cls) -> list[tuple[str, str]]:
        """
        Create a list of default status mappings.
        
        Returns:
            list[tuple[str, str]]: List of (original_status, normalized_status) tuples
        """
        return [
            ("OK", "Accepted"),
            ("Accepted", "Accepted"),
            ("Approved", "Accepted"),
            ("Rejected", "Rejected"),
            ("Clarification needed", "Clarification"),
            ("Need clarification", "Clarification"),
            ("With comments", "With Comments"),
            ("Conditional", "Conditional Acceptance"),
            ("Pending", "Pending"),
            ("In Review", "In Review"),
        ]
    
    def __repr__(self) -> str:
        return f"<StatusMapping(id={self.id}, {self.original_status} -> {self.normalized_status})>"
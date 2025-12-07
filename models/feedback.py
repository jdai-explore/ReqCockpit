"""
SupplierFeedback model for ReqCockpit

This module defines the SupplierFeedback model used to store and manage
feedback from suppliers on specific requirements.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from .base import Base


class SupplierFeedback(Base):
    """
    Represents feedback from a supplier on a specific requirement.
    
    This model stores the supplier's response to a requirement, including
    their status, comments, and any additional metadata.
    
    Attributes:
        id: Primary key
        master_req_id: Foreign key to the MasterRequirement
        iteration_id: Foreign key to the Iteration
        supplier_id: Foreign key to the Supplier
        supplier_status: Original status provided by the supplier
        supplier_status_normalized: Normalized status value
        supplier_comment: Free-text comment from the supplier
        supplier_updated_at: Timestamp of when the supplier last updated the feedback
        internal_notes: Internal notes about the feedback (not visible to supplier)
        created_at: When the feedback record was created
        updated_at: When the feedback record was last updated
        
    Relationships:
        master_requirement: The requirement this feedback is about
        iteration: The iteration this feedback belongs to
        supplier: The supplier who provided the feedback
    """
    __tablename__ = "supplier_feedback"
    __table_args__ = (
        # Ensure only one feedback per requirement, iteration, and supplier
        Index('idx_feedback_unique', 'master_req_id', 'iteration_id', 'supplier_id', unique=True),
    )
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    master_req_id = Column(
        Integer, 
        ForeignKey('master_requirements.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    iteration_id = Column(
        Integer,
        ForeignKey('iterations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    supplier_id = Column(
        Integer,
        ForeignKey('suppliers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Feedback data
    supplier_status = Column(String(100), nullable=True)  # Original status from supplier
    supplier_status_normalized = Column(String(50), nullable=True)  # Normalized status
    supplier_comment = Column(Text, nullable=True)
    supplier_updated_at = Column(DateTime, nullable=True)  # When supplier last updated
    
    # Internal fields
    internal_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    master_requirement = relationship("MasterRequirement", back_populates="feedback")
    iteration = relationship("Iteration", back_populates="feedback")
    supplier = relationship("Supplier", back_populates="feedback")
    
    def is_accepted(self) -> bool:
        """Check if the feedback indicates acceptance of the requirement."""
        return self.supplier_status_normalized in ["Accepted", "Approved"]
    
    def is_rejected(self) -> bool:
        """Check if the feedback indicates rejection of the requirement."""
        return self.supplier_status_normalized in ["Rejected"]
    
    def needs_clarification(self) -> bool:
        """Check if the feedback indicates a need for clarification."""
        return self.supplier_status_normalized in ["Clarification", "Need Clarification", "With Comments"]
    
    def has_conditional_acceptance(self) -> bool:
        """Check if the feedback indicates conditional acceptance."""
        return self.supplier_status_normalized in ["Conditional Acceptance", "With Comments"]
    
    def get_status_display(self) -> str:
        """
        Get a human-readable status display.
        
        Returns:
            str: The normalized status if available, otherwise the original status.
        """
        return self.supplier_status_normalized or self.supplier_status or "No Status"
    
    def __repr__(self) -> str:
        return f"<SupplierFeedback(id={self.id}, req_id={self.master_req_id}, " \
               f"supplier_id={self.supplier_id}, status='{self.supplier_status}')>"
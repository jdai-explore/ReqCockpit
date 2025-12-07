"""
Iteration model for ReqCockpit
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base


class Iteration(Base):
    """
    Represents a time-based iteration in the SRC process
    
    Each supplier import must be tagged with an iteration to maintain
    a complete audit trail of requirement status changes over time.
    
    Examples:
        - I-001_Initial_RFQ
        - I-002_Technical_Review
        - I-003_Final_Quotes
    
    Attributes:
        id: Primary key
        project_id: Foreign key to Project
        iteration_id: Unique human-readable identifier (e.g., "I-001_Initial")
        description: Optional detailed description of iteration purpose
        created_at: Timestamp when iteration was created
        
    Relationships:
        project: Parent Project
        supplier_feedback: All feedback imported in this iteration
        custre_decisions: All decisions made in this iteration
    """
    __tablename__ = "iterations"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    project_id = Column(
        Integer, 
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False, 
        index=True
    )
    
    # Iteration identification
    iteration_id = Column(
        String(100), 
        nullable=False, 
        unique=True, 
        index=True,
        comment="Unique iteration identifier (e.g., I-001_Initial)"
    )
    
    description = Column(
        Text, 
        nullable=True,
        comment="Detailed description of iteration purpose"
    )
    
    # Timestamps
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        comment="When iteration was created"
    )
    
    # Relationships
    project = relationship(
        "Project", 
        back_populates="iterations",
        foreign_keys=[project_id]
    )
    
    supplier_feedback = relationship(
        "SupplierFeedback", 
        back_populates="iteration",
        cascade="all, delete-orphan", 
        lazy="dynamic",
        foreign_keys="SupplierFeedback.iteration_id"
    )
    
    custre_decisions = relationship(
        "CustREDecision", 
        back_populates="iteration",
        cascade="all, delete-orphan", 
        lazy="dynamic",
        foreign_keys="CustREDecision.iteration_id"
    )
    
    def __repr__(self):
        return f"<Iteration(id={self.id}, iteration_id='{self.iteration_id}')>"
    
    def __str__(self):
        return self.iteration_id
    
    def to_dict(self):
        """Convert iteration to dictionary for serialization"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'iteration_id': self.iteration_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_feedback_count(self):
        """Get count of feedback entries in this iteration"""
        return self.supplier_feedback.count()
    
    def get_decision_count(self):
        """Get count of decisions made in this iteration"""
        return self.custre_decisions.count()
    
    @staticmethod
    def validate_iteration_id(iteration_id: str) -> bool:
        """
        Validate iteration ID format
        
        Args:
            iteration_id: ID to validate
            
        Returns:
            True if valid format, False otherwise
        """
        import re
        from config import ITERATION_ID_PATTERN
        
        return bool(re.match(ITERATION_ID_PATTERN, iteration_id))
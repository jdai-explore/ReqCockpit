"""
Master requirement model for ReqCockpit
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class MasterRequirement(Base):
    """
    Master requirement from the OEM/customer specification
    
    This is the source of truth that suppliers respond to.
    Stores the complete ReqIF requirement data including all attributes.
    
    Each master requirement is uniquely identified by its ReqIF ID within
    the project context. Suppliers provide feedback on these requirements
    across multiple iterations.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to Project
        reqif_id: ReqIF IDENTIFIER field (unique within project)
        reqif_internal_id: Internal ID if different from IDENTIFIER
        requirement_type: Type from ReqIF-WF.Type attribute
        text_content: Main requirement text (extracted from various fields)
        raw_attributes: Complete ReqIF attributes stored as JSON
        created_at: Timestamp when requirement was imported
        
    Relationships:
        project: Parent Project
        supplier_feedback: All supplier feedback for this requirement
        custre_decisions: All CustRE decisions for this requirement
    """
    __tablename__ = "master_requirements"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    project_id = Column(
        Integer, 
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False, 
        index=True,
        comment="Reference to parent project"
    )
    
    # ReqIF identification
    reqif_id = Column(
        String(200), 
        nullable=False, 
        index=True,
        comment="ReqIF IDENTIFIER field (unique within project)"
    )
    
    reqif_internal_id = Column(
        String(200), 
        nullable=True,
        comment="Internal ID if different from IDENTIFIER"
    )
    
    # Requirement content
    requirement_type = Column(
        String(100), 
        nullable=True,
        comment="Requirement type from ReqIF-WF.Type"
    )
    
    text_content = Column(
        Text, 
        nullable=True,
        comment="Main requirement text (plain text extraction)"
    )
    
    # Complete ReqIF attributes stored as JSON
    raw_attributes = Column(
        JSON, 
        nullable=True,
        comment="All ReqIF attributes in original structure"
    )
    
    # Timestamps
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="When requirement was imported"
    )
    
    # Relationships
    project = relationship(
        "Project", 
        back_populates="master_requirements",
        foreign_keys=[project_id]
    )
    
    supplier_feedback = relationship(
        "SupplierFeedback", 
        back_populates="master_requirement",
        cascade="all, delete-orphan", 
        lazy="dynamic",
        foreign_keys="SupplierFeedback.master_req_id"
    )
    
    custre_decisions = relationship(
        "CustREDecision", 
        back_populates="master_requirement",
        cascade="all, delete-orphan", 
        lazy="dynamic",
        foreign_keys="CustREDecision.master_req_id"
    )
    
    # Constraints and indexes
    __table_args__ = (
        # Ensure ReqIF ID is unique within project
        UniqueConstraint('project_id', 'reqif_id', name='uq_requirement_project_reqif'),
        
        # Performance indexes
        Index('idx_requirement_reqif_id', 'reqif_id'),
        Index('idx_requirement_type', 'requirement_type'),
    )
    
    def __repr__(self):
        return f"<MasterRequirement(id={self.id}, reqif_id='{self.reqif_id}')>"
    
    def __str__(self):
        text_preview = self.text_content[:50] if self.text_content else "No text"
        return f"{self.reqif_id}: {text_preview}..."
    
    def to_dict(self):
        """Convert requirement to dictionary for serialization"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'reqif_id': self.reqif_id,
            'reqif_internal_id': self.reqif_internal_id,
            'requirement_type': self.requirement_type,
            'text_content': self.text_content,
            'raw_attributes': self.raw_attributes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_feedback_for_iteration(self, iteration_id: int):
        """
        Get all supplier feedback for this requirement in a specific iteration
        
        Args:
            iteration_id: Database ID of iteration
            
        Returns:
            List of SupplierFeedback objects
        """
        return self.supplier_feedback.filter_by(iteration_id=iteration_id).all()
    
    def get_decision_for_iteration(self, iteration_id: int):
        """
        Get CustRE decision for this requirement in a specific iteration
        
        Args:
            iteration_id: Database ID of iteration
            
        Returns:
            CustREDecision object or None
        """
        return self.custre_decisions.filter_by(iteration_id=iteration_id).first()
    
    def has_feedback_in_iteration(self, iteration_id: int) -> bool:
        """Check if any feedback exists for this requirement in iteration"""
        return self.supplier_feedback.filter_by(iteration_id=iteration_id).count() > 0
    
    def has_decision_in_iteration(self, iteration_id: int) -> bool:
        """Check if decision exists for this requirement in iteration"""
        return self.custre_decisions.filter_by(iteration_id=iteration_id).count() > 0
    
    def get_attribute(self, key: str, default=None):
        """
        Get specific attribute from raw_attributes
        
        Args:
            key: Attribute key to retrieve
            default: Default value if key not found
            
        Returns:
            Attribute value or default
        """
        if not self.raw_attributes:
            return default
        return self.raw_attributes.get(key, default)
    
    def get_text_preview(self, max_length: int = 100) -> str:
        """
        Get truncated text content for display
        
        Args:
            max_length: Maximum length of preview
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if not self.text_content:
            return "No text content"
        
        if len(self.text_content) <= max_length:
            return self.text_content
        
        return self.text_content[:max_length] + "..."
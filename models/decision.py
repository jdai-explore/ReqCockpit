"""
CustREDecision model for ReqCockpit
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base


class CustREDecision(Base):
    """
    Customer Requirements Engineer's final decision on a requirement
    
    Records the CustRE's resolution for a specific requirement in an iteration.
    Provides complete audit trail with rationale for all decisions.
    
    This model enables:
    - Tracking final decisions across iterations
    - Complete audit trail for regulatory compliance (ISO 26262)
    - Historical analysis of decision patterns
    - Export of consolidated results
    
    Attributes:
        id: Primary key
        master_req_id: Foreign key to MasterRequirement
        iteration_id: Foreign key to Iteration
        decision_status: Final decision (Accepted/Rejected/Modified/Deferred)
        action_note: Detailed rationale and next steps
        decided_by: Username/identifier of decision maker
        decided_at: Timestamp when decision was made
        
    Relationships:
        master_requirement: The requirement this decision is about
        iteration: The iteration this decision belongs to
        
    Decision Status Values:
        - Accepted: Requirement accepted as-is
        - Rejected: Requirement rejected, will not be implemented
        - Modified: Requirement accepted with modifications
        - Deferred: Decision postponed to later iteration
    """
    __tablename__ = "custre_decisions"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    master_req_id = Column(
        Integer, 
        ForeignKey('master_requirements.id', ondelete='CASCADE'),
        nullable=False, 
        index=True,
        comment="Reference to master requirement"
    )
    
    iteration_id = Column(
        Integer, 
        ForeignKey('iterations.id', ondelete='CASCADE'),
        nullable=False, 
        index=True,
        comment="Reference to iteration when decision was made"
    )
    
    # Decision data
    decision_status = Column(
        String(50), 
        nullable=False,
        comment="Final decision: Accepted/Rejected/Modified/Deferred"
    )
    
    action_note = Column(
        Text, 
        nullable=True,
        comment="Detailed rationale, modifications, or next steps"
    )
    
    # Audit information
    decided_by = Column(
        String(100), 
        nullable=True,
        comment="Username or identifier of person who made decision"
    )
    
    decided_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when decision was made"
    )
    
    # Additional metadata
    previous_decision_id = Column(
        Integer,
        ForeignKey('custre_decisions.id', ondelete='SET NULL'),
        nullable=True,
        comment="Link to previous decision if this is a revision"
    )
    
    # Relationships
    master_requirement = relationship(
        "MasterRequirement", 
        back_populates="custre_decisions",
        foreign_keys=[master_req_id]
    )
    
    iteration = relationship(
        "Iteration", 
        back_populates="custre_decisions",
        foreign_keys=[iteration_id]
    )
    
    previous_decision = relationship(
        "CustREDecision",
        remote_side=[id],
        foreign_keys=[previous_decision_id]
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_decision_req_iter', 'master_req_id', 'iteration_id'),
        Index('idx_decision_status', 'decision_status'),
        Index('idx_decision_decided_at', 'decided_at'),
    )
    
    def __repr__(self):
        return (f"<CustREDecision(id={self.id}, "
                f"req={self.master_req_id}, "
                f"status='{self.decision_status}')>")
    
    def __str__(self):
        return f"{self.decision_status}: {self.action_note[:50] if self.action_note else 'No note'}"
    
    def to_dict(self):
        """Convert decision to dictionary for serialization"""
        return {
            'id': self.id,
            'master_req_id': self.master_req_id,
            'iteration_id': self.iteration_id,
            'decision_status': self.decision_status,
            'action_note': self.action_note,
            'decided_by': self.decided_by,
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'previous_decision_id': self.previous_decision_id
        }
    
    def is_accepted(self) -> bool:
        """Check if decision is Accepted"""
        return self.decision_status == "Accepted"
    
    def is_rejected(self) -> bool:
        """Check if decision is Rejected"""
        return self.decision_status == "Rejected"
    
    def is_modified(self) -> bool:
        """Check if decision is Modified"""
        return self.decision_status == "Modified"
    
    def is_deferred(self) -> bool:
        """Check if decision is Deferred"""
        return self.decision_status == "Deferred"
    
    def has_note(self) -> bool:
        """Check if decision has an action note"""
        return bool(self.action_note and self.action_note.strip())
    
    def get_summary(self) -> str:
        """
        Get brief summary of decision
        
        Returns:
            Summary string suitable for display
        """
        summary = self.decision_status
        if self.decided_by:
            summary += f" by {self.decided_by}"
        if self.decided_at:
            summary += f" on {self.decided_at.strftime('%Y-%m-%d')}"
        return summary
    
    @staticmethod
    def get_valid_statuses():
        """
        Get list of valid decision statuses
        
        Returns:
            List of valid status strings
        """
        return ["Accepted", "Rejected", "Modified", "Deferred"]
    
    @staticmethod
    def validate_status(status: str) -> bool:
        """
        Validate if status is valid
        
        Args:
            status: Status string to validate
            
        Returns:
            True if valid, False otherwise
        """
        return status in CustREDecision.get_valid_statuses()
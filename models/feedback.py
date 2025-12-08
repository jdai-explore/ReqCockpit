"""
SupplierFeedback model for ReqCockpit
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey,
    Index, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .base import Base


class SupplierFeedback(Base):
    """
    Represents a single supplier's feedback on a specific requirement
    in a given iteration.

    This is the core data model for aggregating supplier responses.

    Attributes:
        id: Primary key
        master_req_id: Foreign key to MasterRequirement
        supplier_id: Foreign key to Supplier
        iteration_id: Foreign key to Iteration
        status: The supplier's original status (e.g., "Compliant", "For Review")
        harmonized_status: The application's normalized status (e.g., "Accepted", "Clarification")
        comment: Supplier's textual feedback or rationale
        raw_attributes: Complete original attributes from supplier ReqIF as JSON
        created_at: Timestamp when feedback was imported

    Relationships:
        master_requirement: The requirement this feedback is about
        supplier: The supplier who provided this feedback
        iteration: The iteration this feedback belongs to
    """
    __tablename__ = "supplier_feedback"

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

    supplier_id = Column(
        Integer,
        ForeignKey('suppliers.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to supplier providing feedback"
    )

    iteration_id = Column(
        Integer,
        ForeignKey('iterations.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Reference to iteration of this feedback"
    )

    # Feedback data
    status = Column(
        String(100),
        nullable=True,
        comment="Original status from supplier's ReqIF"
    )

    harmonized_status = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Normalized status (e.g., Accepted, Clarification)"
    )

    comment = Column(
        Text,
        nullable=True,
        comment="Supplier's textual feedback or rationale"
    )

    # Complete supplier attributes stored as JSON
    raw_attributes = Column(
        JSON,
        nullable=True,
        comment="All supplier ReqIF attributes in original structure"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when feedback was imported"
    )

    # Relationships
    master_requirement = relationship(
        "MasterRequirement",
        back_populates="supplier_feedback",
        foreign_keys=[master_req_id]
    )

    supplier = relationship(
        "Supplier",
        back_populates="supplier_feedback",
        foreign_keys=[supplier_id]
    )

    iteration = relationship(
        "Iteration",
        back_populates="supplier_feedback",
        foreign_keys=[iteration_id]
    )

    # Constraints and indexes
    __table_args__ = (
        # Ensure feedback is unique for a req/supplier/iteration combo
        UniqueConstraint(
            'master_req_id', 'supplier_id', 'iteration_id',
            name='uq_feedback_req_supp_iter'
        ),

        # Performance indexes
        Index('idx_feedback_harmonized_status', 'harmonized_status'),
    )

    def __repr__(self):
        return (f"<SupplierFeedback(id={self.id}, "
                f"req={self.master_req_id}, "
                f"supp={self.supplier_id}, "
                f"iter={self.iteration_id})>")

    def __str__(self):
        return f"{self.harmonized_status}: {self.comment[:50] if self.comment else 'No comment'}"

    def to_dict(self):
        """Convert feedback to dictionary for serialization"""
        return {
            'id': self.id,
            'master_req_id': self.master_req_id,
            'supplier_id': self.supplier_id,
            'iteration_id': self.iteration_id,
            'status': self.status,
            'harmonized_status': self.harmonized_status,
            'comment': self.comment,
            'raw_attributes': self.raw_attributes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def has_comment(self) -> bool:
        """Check if feedback includes a textual comment"""
        return bool(self.comment and self.comment.strip())

    def is_accepted(self) -> bool:
        """Check if feedback is Accepted"""
        return self.harmonized_status == "Accepted"

    def needs_clarification(self) -> bool:
        """Check if feedback needs clarification"""
        return self.harmonized_status == "Clarification"

    def is_rejected(self) -> bool:
        """Check if feedback is Rejected"""
        return self.harmonized_status == "Rejected"

    def get_attribute(self, key: str, default=None):
        """
        Get a specific attribute from the raw supplier attributes

        Args:
            key: Attribute key to retrieve
            default: Default value if key not found

        Returns:
            Attribute value or default
        """
        if not self.raw_attributes:
            return default
        return self.raw_attributes.get(key, default)

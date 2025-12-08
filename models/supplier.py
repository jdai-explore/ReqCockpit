"""
Supplier model for ReqCockpit
"""
import re
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey,
    Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .base import Base


class Supplier(Base):
    """
    Represents a single supplier in a project

    Each project can have multiple suppliers providing feedback on
    the master requirements list. This model stores supplier-specific
    information.

    Attributes:
        id: Primary key
        project_id: Foreign key to Project
        name: Unique supplier name within the project
        supplier_code: Optional internal supplier identifier
        contact_person: Main contact person at supplier
        contact_email: Email address of contact person
        created_at: Timestamp when supplier was added

    Relationships:
        project: Parent Project
        supplier_feedback: All feedback provided by this supplier
    """
    __tablename__ = "suppliers"

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

    # Supplier identification
    name = Column(
        String(200),
        nullable=False,
        comment="Supplier's full legal name"
    )

    supplier_code = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Internal supplier code or number"
    )

    # Contact information
    contact_person = Column(
        String(150),
        nullable=True,
        comment="Main contact person at the supplier"
    )

    contact_email = Column(
        String(150),
        nullable=True,
        comment="Email address of the contact person"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when supplier was added to project"
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="suppliers",
        foreign_keys=[project_id]
    )

    supplier_feedback = relationship(
        "SupplierFeedback",
        back_populates="supplier",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="SupplierFeedback.supplier_id"
    )

    # Constraints and indexes
    __table_args__ = (
        # Ensure supplier name is unique within a project
        UniqueConstraint('project_id', 'name', name='uq_supplier_project_name'),

        # Performance indexes
        Index('idx_supplier_name', 'name'),
        Index('idx_supplier_code', 'supplier_code'),
    )

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return self.name

    def to_dict(self):
        """Convert supplier to dictionary for serialization"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'supplier_code': self.supplier_code,
            'contact_person': self.contact_person,
            'contact_email': self.contact_email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_feedback_count(self):
        """Get the total number of feedback entries from this supplier"""
        return self.supplier_feedback.count()

    def get_feedback_in_iteration(self, iteration_id: int):
        """
        Get feedback from this supplier for a specific iteration

        Args:
            iteration_id: Database ID of the iteration

        Returns:
            List of SupplierFeedback objects
        """
        return self.supplier_feedback.filter_by(iteration_id=iteration_id).all()

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate supplier name

        Args:
            name: Supplier name to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(name and len(name.strip()) > 0)

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email:
            return True # Email is optional
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

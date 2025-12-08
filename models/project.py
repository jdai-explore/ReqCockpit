"""
Project model for ReqCockpit
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import relationship
from .base import Base


class Project(Base):
    """
    Represents a single project in ReqCockpit

    A project is the top-level container for all data related to a
    specific vehicle or system, including requirements, suppliers,
    iterations, and decisions.

    Attributes:
        id: Primary key
        name: Unique project name
        description: Optional detailed project description
        db_path: Full path to the project's SQLite database file
        created_at: Timestamp when project was created
        last_modified_at: Timestamp of last modification

    Relationships:
        iterations: All iterations within this project
        master_requirements: All master requirements for this project
        suppliers: All suppliers associated with this project
    """
    __tablename__ = "projects"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Project details
    name = Column(
        String(200),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique project name"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Detailed project description"
    )

    db_path = Column(
        String(500),
        nullable=False,
        unique=True,
        comment="Full path to the project's SQLite database file"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="When project was created"
    )

    last_modified_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="When project was last modified"
    )

    # Relationships
    iterations = relationship(
        "Iteration",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    master_requirements = relationship(
        "MasterRequirement",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    suppliers = relationship(
        "Supplier",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    __table_args__ = (
        Index('idx_project_name', 'name'),
        Index('idx_project_last_modified', 'last_modified_at'),
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return self.name

    def to_dict(self):
        """Convert project to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'db_path': self.db_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_modified_at': self.last_modified_at.isoformat() if self.last_modified_at else None
        }

    def get_iteration_count(self):
        """Get the number of iterations in this project"""
        return self.iterations.count()

    def get_requirement_count(self):
        """Get the number of master requirements in this project"""
        return self.master_requirements.count()

    def get_supplier_count(self):
        """Get the number of suppliers in this project"""
        return self.suppliers.count()

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate project name

        Args:
            name: Project name to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(name and len(name.strip()) > 0)

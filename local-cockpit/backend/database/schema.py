from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, JSON, ForeignKey, TEXT, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_opened = Column(TIMESTAMP)
    master_spec_filename = Column(String)
    master_spec_imported_at = Column(TIMESTAMP)

class Iteration(Base):
    __tablename__ = 'iterations'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    iteration_id = Column(String, nullable=False, unique=True)
    description = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    __table_args__ = (UniqueConstraint('project_id', 'iteration_id', name='_project_iteration_uc'),)

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String, nullable=False)
    short_name = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    __table_args__ = (UniqueConstraint('project_id', 'name', name='_project_supplier_uc'),)

class MasterRequirement(Base):
    __tablename__ = 'master_requirements'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    reqif_id = Column(String, nullable=False)
    reqif_internal_id = Column(String)
    requirement_type = Column(String)
    text_content = Column(TEXT)
    raw_attributes = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    __table_args__ = (UniqueConstraint('project_id', 'reqif_id', name='_project_reqif_id_uc'),)

class SupplierFeedback(Base):
    __tablename__ = 'supplier_feedback'
    id = Column(Integer, primary_key=True)
    master_req_id = Column(Integer, ForeignKey('master_requirements.id'), nullable=False)
    iteration_id = Column(Integer, ForeignKey('iterations.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    supplier_status = Column(String)
    supplier_status_normalized = Column(String)
    supplier_comment = Column(TEXT)
    raw_attributes = Column(JSON)
    imported_at = Column(TIMESTAMP, server_default=func.now())
    __table_args__ = (UniqueConstraint('master_req_id', 'iteration_id', 'supplier_id', name='_feedback_uc'),)

class CustREDecision(Base):
    __tablename__ = 'custre_decisions'
    id = Column(Integer, primary_key=True)
    master_req_id = Column(Integer, ForeignKey('master_requirements.id'), nullable=False)
    iteration_id = Column(Integer, ForeignKey('iterations.id'), nullable=False)
    decision_status = Column(String, nullable=False)
    action_note = Column(TEXT)
    decided_by = Column(String)
    decided_at = Column(TIMESTAMP, server_default=func.now())

class StatusMapping(Base):
    __tablename__ = 'status_mappings'
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    original_status = Column(String, nullable=False)
    normalized_status = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint('supplier_id', 'original_status', name='_mapping_uc'),)


def create_database(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)

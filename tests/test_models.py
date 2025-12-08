"""
Test suite for ReqCockpit models

Verifies all database models, relationships, and operations work correctly.
"""
import pytest
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path

# Import models
from models import (
    Base, DatabaseManager, db_manager,
    Project, Iteration, Supplier,
    MasterRequirement, SupplierFeedback, CustREDecision
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
        db_path = f.name
    
    # Create database
    db_manager.create_database(db_path)
    db_manager.connect(db_path)
    
    yield db_path
    
    # Cleanup
    db_manager.disconnect()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def sample_project(temp_db):
    """Create a sample project for testing"""
    session = db_manager.get_session()
    
    project = Project(
        name="Test Project",
        description="A test project for unit tests",
        db_path=temp_db
    )
    session.add(project)
    session.commit()
    
    project_id = project.id
    session.close()
    
    return project_id


class TestDatabaseManager:
    """Test DatabaseManager functionality"""
    
    def test_create_database(self, temp_db):
        """Test database creation"""
        assert os.path.exists(temp_db)
        assert db_manager.current_db_path == temp_db
    
    def test_get_session(self, temp_db):
        """Test session creation"""
        session = db_manager.get_session()
        assert session is not None
        session.close()
    
    def test_backup_database(self, temp_db):
        """Test database backup"""
        backup_path = temp_db + ".test_backup"
        result = db_manager.backup_database(backup_path)
        
        assert result is True
        assert os.path.exists(backup_path)
        
        # Cleanup
        if os.path.exists(backup_path):
            os.remove(backup_path)


class TestProjectModel:
    """Test Project model"""
    
    def test_create_project(self, temp_db):
        """Test creating a project"""
        session = db_manager.get_session()
        
        project = Project(
            name="My Project",
            description="Test description",
            db_path=temp_db
        )
        session.add(project)
        session.commit()
        
        assert project.id is not None
        assert project.name == "My Project"
        assert project.created_at is not None
        
        session.close()
    
    def test_project_to_dict(self, sample_project):
        """Test project serialization"""
        session = db_manager.get_session()
        
        project = session.query(Project).filter_by(id=sample_project).first()
        project_dict = project.to_dict()
        
        assert 'id' in project_dict
        assert 'name' in project_dict
        assert project_dict['name'] == "Test Project"
        
        session.close()
    
    def test_project_relationships(self, sample_project):
        """Test project can access related entities"""
        session = db_manager.get_session()
        
        project = session.query(Project).filter_by(id=sample_project).first()
        
        # Should be able to access (even if empty)
        assert project.iterations.count() == 0
        assert project.suppliers.count() == 0
        assert project.master_requirements.count() == 0
        
        session.close()


class TestIterationModel:
    """Test Iteration model"""
    
    def test_create_iteration(self, sample_project):
        """Test creating an iteration"""
        session = db_manager.get_session()
        
        iteration = Iteration(
            project_id=sample_project,
            iteration_id="I-001_Initial",
            description="First iteration"
        )
        session.add(iteration)
        session.commit()
        
        assert iteration.id is not None
        assert iteration.iteration_id == "I-001_Initial"
        
        session.close()
    
    def test_iteration_validation(self):
        """Test iteration ID validation"""
        assert Iteration.validate_iteration_id("I-001_Initial") is True
        assert Iteration.validate_iteration_id("I-999_Test_Run") is True
        assert Iteration.validate_iteration_id("invalid") is False


class TestSupplierModel:
    """Test Supplier model"""
    
    def test_create_supplier(self, sample_project):
        """Test creating a supplier"""
        session = db_manager.get_session()
        
        supplier = Supplier(
            project_id=sample_project,
            name="ACME Corp",
            supplier_code="ACME"
        )
        session.add(supplier)
        session.commit()
        
        assert supplier.id is not None
        assert supplier.name == "ACME Corp"
        assert supplier.supplier_code == "ACME"
        
        session.close()


class TestMasterRequirementModel:
    """Test MasterRequirement model"""
    
    def test_create_requirement(self, sample_project):
        """Test creating a master requirement"""
        session = db_manager.get_session()
        
        requirement = MasterRequirement(
            project_id=sample_project,
            reqif_id="REQ-001",
            requirement_type="Functional",
            text_content="The system shall...",
            raw_attributes={"attr1": "value1"}
        )
        session.add(requirement)
        session.commit()
        
        assert requirement.id is not None
        assert requirement.reqif_id == "REQ-001"
        assert requirement.text_content == "The system shall..."
        
        session.close()
    
    def test_requirement_text_preview(self, sample_project):
        """Test text preview generation"""
        session = db_manager.get_session()
        
        long_text = "A" * 200
        requirement = MasterRequirement(
            project_id=sample_project,
            reqif_id="REQ-002",
            text_content=long_text
        )
        
        preview = requirement.get_text_preview(50)
        assert len(preview) <= 53  # 50 + "..."
        assert preview.endswith("...")
        
        session.close()
    
    def test_requirement_get_attribute(self, sample_project):
        """Test attribute retrieval"""
        session = db_manager.get_session()
        
        requirement = MasterRequirement(
            project_id=sample_project,
            reqif_id="REQ-003",
            raw_attributes={"key1": "value1", "key2": "value2"}
        )
        
        assert requirement.get_attribute("key1") == "value1"
        assert requirement.get_attribute("key3", "default") == "default"
        
        session.close()


class TestSupplierFeedbackModel:
    """Test SupplierFeedback model"""
    
    def test_create_feedback(self, sample_project):
        """Test creating supplier feedback"""
        session = db_manager.get_session()
        
        # Create dependencies
        iteration = Iteration(
            project_id=sample_project,
            iteration_id="I-001_Test"
        )
        session.add(iteration)
        
        supplier = Supplier(
            project_id=sample_project,
            name="Test Supplier"
        )
        session.add(supplier)
        
        requirement = MasterRequirement(
            project_id=sample_project,
            reqif_id="REQ-001"
        )
        session.add(requirement)
        session.flush()
        
        # Create feedback
        feedback = SupplierFeedback(
            master_req_id=requirement.id,
            iteration_id=iteration.id,
            supplier_id=supplier.id,
            status="OK",
            harmonized_status="Accepted",
            comment="Looks good"
        )
        session.add(feedback)
        session.commit()
        
        assert feedback.id is not None
        assert feedback.status == "OK"
        assert feedback.is_accepted() is True
        
        session.close()
    
    def test_feedback_status_checks(self, sample_project):
        """Test status checking methods"""
        feedback = SupplierFeedback(
            master_req_id=1,
            iteration_id=1,
            supplier_id=1,
            harmonized_status="Clarification"
        )
        
        assert feedback.is_accepted() is False
        assert feedback.needs_clarification() is True
        assert feedback.is_rejected() is False


class TestCustREDecisionModel:
    """Test CustREDecision model"""
    
    def test_create_decision(self, sample_project):
        """Test creating a CustRE decision"""
        session = db_manager.get_session()
        
        # Create dependencies
        iteration = Iteration(
            project_id=sample_project,
            iteration_id="I-001_Test"
        )
        session.add(iteration)
        
        requirement = MasterRequirement(
            project_id=sample_project,
            reqif_id="REQ-001"
        )
        session.add(requirement)
        session.flush()
        
        # Create decision
        decision = CustREDecision(
            master_req_id=requirement.id,
            iteration_id=iteration.id,
            decision_status="Accepted",
            action_note="Approved as specified",
            decided_by="john.doe"
        )
        session.add(decision)
        session.commit()
        
        assert decision.id is not None
        assert decision.decision_status == "Accepted"
        assert decision.is_accepted() is True
        
        session.close()
    
    def test_decision_validation(self):
        """Test decision status validation"""
        assert CustREDecision.validate_status("Accepted") is True
        assert CustREDecision.validate_status("Rejected") is True
        assert CustREDecision.validate_status("Modified") is True
        assert CustREDecision.validate_status("Deferred") is True
        assert CustREDecision.validate_status("Invalid") is False
    
    def test_decision_summary(self, sample_project):
        """Test decision summary generation"""
        decision = CustREDecision(
            master_req_id=1,
            iteration_id=1,
            decision_status="Modified",
            decided_by="jane.smith",
            decided_at=datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
        )
        
        summary = decision.get_summary()
        assert "Modified" in summary
        assert "jane.smith" in summary
        assert "2024-01-15" in summary


class TestRelationships:
    """Test relationships between models"""
    
    def test_project_to_iteration(self, sample_project):
        """Test project can access iterations"""
        session = db_manager.get_session()
        
        project = session.query(Project).filter_by(id=sample_project).first()
        
        iteration = Iteration(
            project_id=project.id,
            iteration_id="I-001_Test"
        )
        session.add(iteration)
        session.commit()
        
        assert project.iterations.count() == 1
        assert project.get_iteration_count() == 1
        
        session.close()
    
    def test_requirement_to_feedback(self, sample_project):
        """Test requirement can access feedback"""
        session = db_manager.get_session()
        
        # Setup
        iteration = Iteration(
            project_id=sample_project,
            iteration_id="I-001_Test"
        )
        session.add(iteration)
        
        supplier = Supplier(
            project_id=sample_project,
            name="Test Supplier"
        )
        session.add(supplier)
        
        requirement = MasterRequirement(
            project_id=sample_project,
            reqif_id="REQ-001"
        )
        session.add(requirement)
        session.flush()
        
        # Add feedback
        feedback = SupplierFeedback(
            master_req_id=requirement.id,
            iteration_id=iteration.id,
            supplier_id=supplier.id,
            status="OK"
        )
        session.add(feedback)
        session.commit()
        
        # Test access
        assert requirement.supplier_feedback.count() == 1
        assert requirement.has_feedback_in_iteration(iteration.id) is True
        
        feedback_list = requirement.get_feedback_for_iteration(iteration.id)
        assert len(feedback_list) == 1
        
        session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

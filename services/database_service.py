"""
Database service for ReqCockpit
Provides high-level database operations for the application
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.base import db_manager
from models.project import Project
from models.iteration import Iteration
from models.supplier import Supplier, StatusMapping
from models.requirement import MasterRequirement
from models.feedback import SupplierFeedback
from models.decision import CustREDecision
from config import DB_EXTENSION

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    High-level database operations for ReqCockpit
    
    Provides a clean API for the UI layer to interact with the database
    without direct SQLAlchemy knowledge required.
    """
    
    @staticmethod
    def create_project(name: str, directory: str, description: str = None) -> Dict[str, Any]:
        """
        Create a new project with database
        
        Args:
            name: Project name (will be sanitized for filename)
            directory: Directory where database will be created
            description: Optional project description
            
        Returns:
            Dictionary with success status, message, and project data
        """
        try:
            # Sanitize project name for filename
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            
            # Create database file path
            db_filename = f"{safe_name}{DB_EXTENSION}"
            db_path = Path(directory) / db_filename
            
            # Check if file already exists
            if db_path.exists():
                return {
                    'success': False,
                    'message': f"Project file already exists: {db_path}",
                    'project': None
                }
            
            # Create database
            if not db_manager.create_database(str(db_path)):
                return {
                    'success': False,
                    'message': "Failed to create database file",
                    'project': None
                }
            
            # Connect to new database
            if not db_manager.connect(str(db_path)):
                return {
                    'success': False,
                    'message': "Failed to connect to new database",
                    'project': None
                }
            
            # Create project record
            session = db_manager.get_session()
            try:
                project = Project(
                    name=name,
                    description=description,
                    created_at=datetime.utcnow(),
                    last_opened=datetime.utcnow()
                )
                session.add(project)
                session.commit()
                
                project_dict = project.to_dict()
                project_dict['db_path'] = str(db_path)
                
                return {
                    'success': True,
                    'message': f"Project '{name}' created successfully",
                    'project': project_dict
                }
                
            except IntegrityError as e:
                session.rollback()
                return {
                    'success': False,
                    'message': f"Project name already exists: {e}",
                    'project': None
                }
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                'success': False,
                'message': f"Error creating project: {str(e)}",
                'project': None
            }
    
    @staticmethod
    def open_project(db_path: str) -> Dict[str, Any]:
        """
        Open an existing project
        
        Args:
            db_path: Path to the project database file
            
        Returns:
            Dictionary with success status, message, and project data
        """
        try:
            # Check if file exists
            if not Path(db_path).exists():
                return {
                    'success': False,
                    'message': f"Project file not found: {db_path}",
                    'project': None
                }
            
            # Connect to database
            if not db_manager.connect(db_path):
                return {
                    'success': False,
                    'message': "Failed to connect to database",
                    'project': None
                }
            
            # Load project record
            session = db_manager.get_session()
            try:
                project = session.query(Project).first()
                
                if not project:
                    return {
                        'success': False,
                        'message': "No project found in database",
                        'project': None
                    }
                
                # Update last opened timestamp
                project.last_opened = datetime.utcnow()
                session.commit()
                
                project_dict = project.to_dict()
                project_dict['db_path'] = db_path
                
                return {
                    'success': True,
                    'message': f"Project '{project.name}' opened successfully",
                    'project': project_dict
                }
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error opening project: {e}")
            return {
                'success': False,
                'message': f"Error opening project: {str(e)}",
                'project': None
            }
    
    @staticmethod
    def get_project_info() -> Optional[Dict[str, Any]]:
        """
        Get current project information
        
        Returns:
            Project dictionary or None if no project open
        """
        session = db_manager.get_session()
        if not session:
            return None
            
        try:
            project = session.query(Project).first()
            return project.to_dict() if project else None
        finally:
            session.close()
    
    @staticmethod
    def create_iteration(iteration_id: str, description: str = None) -> Dict[str, Any]:
        """
        Create a new iteration for the current project
        
        Args:
            iteration_id: Unique iteration identifier (e.g., "I-001_Initial")
            description: Optional iteration description
            
        Returns:
            Dictionary with success status, message, and iteration data
        """
        session = db_manager.get_session()
        if not session:
            return {
                'success': False,
                'message': "No database connection",
                'iteration': None
            }
        
        try:
            # Get current project
            project = session.query(Project).first()
            if not project:
                return {
                    'success': False,
                    'message': "No project found",
                    'iteration': None
                }
            
            # Check if iteration already exists
            existing = session.query(Iteration).filter_by(
                iteration_id=iteration_id
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'message': f"Iteration '{iteration_id}' already exists",
                    'iteration': None
                }
            
            # Create iteration
            iteration = Iteration(
                project_id=project.id,
                iteration_id=iteration_id,
                description=description,
                created_at=datetime.utcnow()
            )
            
            session.add(iteration)
            session.commit()
            
            return {
                'success': True,
                'message': f"Iteration '{iteration_id}' created",
                'iteration': iteration.to_dict()
            }
            
        except IntegrityError:
            session.rollback()
            return {
                'success': False,
                'message': f"Iteration '{iteration_id}' already exists",
                'iteration': None
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating iteration: {e}")
            return {
                'success': False,
                'message': f"Error creating iteration: {str(e)}",
                'iteration': None
            }
        finally:
            session.close()
    
    @staticmethod
    def list_iterations() -> List[Dict[str, Any]]:
        """
        Get all iterations for current project
        
        Returns:
            List of iteration dictionaries
        """
        session = db_manager.get_session()
        if not session:
            return []
        
        try:
            iterations = session.query(Iteration).order_by(
                Iteration.created_at.desc()
            ).all()
            
            return [iter.to_dict() for iter in iterations]
            
        finally:
            session.close()
    
    @staticmethod
    def get_or_create_supplier(name: str, short_name: str = None) -> Optional[int]:
        """
        Get existing supplier or create new one
        
        Args:
            name: Supplier name
            short_name: Optional short name for grid display
            
        Returns:
            Supplier ID or None on error
        """
        session = db_manager.get_session()
        if not session:
            return None
        
        try:
            # Get current project
            project = session.query(Project).first()
            if not project:
                return None
            
            # Check if supplier exists
            supplier = session.query(Supplier).filter_by(
                project_id=project.id,
                name=name
            ).first()
            
            if supplier:
                return supplier.id
            
            # Create new supplier
            supplier = Supplier(
                project_id=project.id,
                name=name,
                short_name=short_name or name[:10],
                created_at=datetime.utcnow()
            )
            
            session.add(supplier)
            session.commit()
            
            return supplier.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting/creating supplier: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def list_suppliers() -> List[Dict[str, Any]]:
        """
        Get all suppliers for current project
        
        Returns:
            List of supplier dictionaries
        """
        session = db_manager.get_session()
        if not session:
            return []
        
        try:
            suppliers = session.query(Supplier).order_by(
                Supplier.name
            ).all()
            
            return [s.to_dict() for s in suppliers]
            
        finally:
            session.close()
    
    @staticmethod
    def close_project():
        """Close the current project and database connection"""
        db_manager.disconnect()
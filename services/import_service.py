"""
Import service for ReqCockpit
Handles ReqIF file parsing and database import operations
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from models.base import db_manager
from models.project import Project
from models.iteration import Iteration
from models.supplier import Supplier
from models.requirement import MasterRequirement
from models.feedback import SupplierFeedback
from parsers.reqif_parser import ReqIFParser
from services.status_harmonizer import harmonizer
from config import BATCH_IMPORT_SIZE

logger = logging.getLogger(__name__)


class ImportService:
    """
    Service for importing ReqIF files into the database
    
    Handles both master specification and supplier feedback imports
    with progress reporting and error handling.
    """
    
    def __init__(self):
        self.parser = ReqIFParser()
    
    def import_master_specification(self, 
                                    file_path: str,
                                    progress_callback: Optional[Callable[[int, int, str], None]] = None
                                   ) -> Dict[str, Any]:
        """
        Import master specification from ReqIF file
        
        Args:
            file_path: Path to master ReqIF file
            progress_callback: Optional callback(current, total, message)
            
        Returns:
            Dictionary with import results
        """
        try:
            # Report start
            if progress_callback:
                progress_callback(0, 100, "Parsing ReqIF file...")
            
            # Parse ReqIF file
            requirements = self.parser.parse_file(file_path)
            
            if not requirements:
                return {
                    'success': False,
                    'message': "No requirements found in file",
                    'imported_count': 0,
                    'warnings': []
                }
            
            if progress_callback:
                progress_callback(30, 100, f"Found {len(requirements)} requirements")
            
            # Get database session
            session = db_manager.get_session()
            if not session:
                return {
                    'success': False,
                    'message': "No database connection",
                    'imported_count': 0
                }
            
            try:
                # Get current project
                project = session.query(Project).first()
                if not project:
                    return {
                        'success': False,
                        'message': "No project found",
                        'imported_count': 0
                    }
                
                # Import requirements in batches
                imported_count = 0
                warnings = []
                
                for i, req in enumerate(requirements):
                    try:
                        # Extract key fields
                        reqif_id = req.get('id') or req.get('identifier')
                        if not reqif_id:
                            warnings.append(f"Requirement {i} missing ID, skipping")
                            continue
                        
                        # Get text content from various possible fields
                        text_content = (
                            req.get('attributes', {}).get('ReqIF.Text') or
                            req.get('attributes', {}).get('Text') or
                            req.get('attributes', {}).get('Description') or
                            self._extract_first_text_attribute(req.get('attributes', {}))
                        )
                        
                        # Get requirement type
                        req_type = (
                            req.get('type') or
                            req.get('attributes', {}).get('ReqIF-WF.Type') or
                            req.get('attributes', {}).get('Type')
                        )
                        
                        # Check if requirement already exists
                        existing = session.query(MasterRequirement).filter_by(
                            project_id=project.id,
                            reqif_id=reqif_id
                        ).first()
                        
                        if existing:
                            # Update existing
                            existing.requirement_type = req_type
                            existing.text_content = text_content
                            existing.raw_attributes = req.get('attributes')
                        else:
                            # Create new
                            master_req = MasterRequirement(
                                project_id=project.id,
                                reqif_id=reqif_id,
                                reqif_internal_id=req.get('identifier'),
                                requirement_type=req_type,
                                text_content=text_content,
                                raw_attributes=req.get('attributes'),
                                created_at=datetime.utcnow()
                            )
                            session.add(master_req)
                        
                        imported_count += 1
                        
                        # Commit in batches
                        if imported_count % BATCH_IMPORT_SIZE == 0:
                            session.commit()
                            if progress_callback:
                                progress = 30 + (50 * imported_count / len(requirements))
                                progress_callback(
                                    int(progress), 100,
                                    f"Imported {imported_count}/{len(requirements)} requirements"
                                )
                    
                    except Exception as e:
                        logger.error(f"Error importing requirement {i}: {e}")
                        warnings.append(f"Failed to import requirement {i}: {str(e)}")
                        continue
                
                # Final commit
                session.commit()
                
                # Update project metadata
                project.master_spec_filename = Path(file_path).name
                project.master_spec_imported_at = datetime.utcnow()
                project.master_spec_requirement_count = imported_count
                session.commit()
                
                if progress_callback:
                    progress_callback(100, 100, "Import complete")
                
                return {
                    'success': True,
                    'message': f"Imported {imported_count} requirements",
                    'imported_count': imported_count,
                    'warnings': warnings
                }
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error during import: {e}")
                return {
                    'success': False,
                    'message': f"Database error: {str(e)}",
                    'imported_count': 0
                }
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error parsing ReqIF file: {e}")
            return {
                'success': False,
                'message': f"Error parsing file: {str(e)}",
                'imported_count': 0
            }
    
    def import_supplier_feedback(self,
                                file_path: str,
                                supplier_name: str,
                                iteration_id: int,
                                progress_callback: Optional[Callable[[int, int, str], None]] = None
                               ) -> Dict[str, Any]:
        """
        Import supplier feedback from ReqIF file
        
        Args:
            file_path: Path to supplier ReqIF file
            supplier_name: Name of the supplier
            iteration_id: Database ID of the iteration
            progress_callback: Optional callback(current, total, message)
            
        Returns:
            Dictionary with import results
        """
        try:
            # Report start
            if progress_callback:
                progress_callback(0, 100, f"Parsing {supplier_name} response...")
            
            # Parse ReqIF file
            requirements = self.parser.parse_file(file_path)
            
            if not requirements:
                return {
                    'success': False,
                    'message': f"No requirements found in {supplier_name} file",
                    'matched_count': 0,
                    'unmatched_count': 0
                }
            
            if progress_callback:
                progress_callback(30, 100, f"Found {len(requirements)} responses")
            
            # Get database session
            session = db_manager.get_session()
            if not session:
                return {
                    'success': False,
                    'message': "No database connection",
                    'matched_count': 0
                }
            
            try:
                # Get current project
                project = session.query(Project).first()
                if not project:
                    return {
                        'success': False,
                        'message': "No project found",
                        'matched_count': 0
                    }
                
                # Get or create supplier
                supplier = session.query(Supplier).filter_by(
                    project_id=project.id,
                    name=supplier_name
                ).first()
                
                if not supplier:
                    supplier = Supplier(
                        project_id=project.id,
                        name=supplier_name,
                        short_name=supplier_name[:10],
                        created_at=datetime.utcnow()
                    )
                    session.add(supplier)
                    session.flush()  # Get supplier ID
                
                # Build master requirements lookup
                master_reqs = session.query(MasterRequirement).filter_by(
                    project_id=project.id
                ).all()
                
                master_lookup = {mr.reqif_id: mr.id for mr in master_reqs}
                
                # Import feedback
                matched_count = 0
                unmatched_count = 0
                warnings = []
                
                for i, req in enumerate(requirements):
                    try:
                        # Extract ReqIF ID
                        reqif_id = req.get('id') or req.get('identifier')
                        if not reqif_id:
                            warnings.append(f"Response {i} missing ID, skipping")
                            unmatched_count += 1
                            continue
                        
                        # Match to master requirement
                        master_req_id = master_lookup.get(reqif_id)
                        if not master_req_id:
                            warnings.append(f"No master requirement for ID: {reqif_id}")
                            unmatched_count += 1
                            continue
                        
                        # Extract supplier status and comment
                        attributes = req.get('attributes', {})
                        supplier_status = (
                            attributes.get('ReqIF-WF.SupplierStatus') or
                            attributes.get('SupplierStatus') or
                            attributes.get('Status')
                        )
                        
                        supplier_comment = (
                            attributes.get('ReqIF-WF.SupplierComment') or
                            attributes.get('SupplierComment') or
                            attributes.get('Comment')
                        )
                        
                        # Normalize status
                        normalized_status = harmonizer.normalize_status(
                            supplier_status, 
                            supplier.id
                        )
                        
                        # Check if feedback already exists
                        existing = session.query(SupplierFeedback).filter_by(
                            master_req_id=master_req_id,
                            iteration_id=iteration_id,
                            supplier_id=supplier.id
                        ).first()
                        
                        if existing:
                            # Update existing
                            existing.supplier_status = supplier_status
                            existing.supplier_status_normalized = normalized_status.value
                            existing.supplier_comment = supplier_comment
                            existing.raw_attributes = attributes
                        else:
                            # Create new
                            feedback = SupplierFeedback(
                                master_req_id=master_req_id,
                                iteration_id=iteration_id,
                                supplier_id=supplier.id,
                                supplier_status=supplier_status,
                                supplier_status_normalized=normalized_status.value,
                                supplier_comment=supplier_comment,
                                raw_attributes=attributes,
                                imported_at=datetime.utcnow()
                            )
                            session.add(feedback)
                        
                        matched_count += 1
                        
                        # Commit in batches
                        if matched_count % BATCH_IMPORT_SIZE == 0:
                            session.commit()
                            if progress_callback:
                                progress = 30 + (60 * matched_count / len(requirements))
                                progress_callback(
                                    int(progress), 100,
                                    f"Matched {matched_count}/{len(requirements)} requirements"
                                )
                    
                    except Exception as e:
                        logger.error(f"Error importing feedback {i}: {e}")
                        warnings.append(f"Failed to import feedback {i}: {str(e)}")
                        unmatched_count += 1
                        continue
                
                # Final commit
                session.commit()
                
                if progress_callback:
                    progress_callback(100, 100, "Import complete")
                
                return {
                    'success': True,
                    'message': f"Matched {matched_count} requirements from {supplier_name}",
                    'matched_count': matched_count,
                    'unmatched_count': unmatched_count,
                    'warnings': warnings
                }
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error during import: {e}")
                return {
                    'success': False,
                    'message': f"Database error: {str(e)}",
                    'matched_count': 0
                }
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error parsing supplier file: {e}")
            return {
                'success': False,
                'message': f"Error parsing file: {str(e)}",
                'matched_count': 0
            }
    
    def _extract_first_text_attribute(self, attributes: Dict[str, Any]) -> Optional[str]:
        """
        Extract first non-empty text attribute from requirements
        
        Args:
            attributes: Dictionary of requirement attributes
            
        Returns:
            First text value found or None
        """
        for key, value in attributes.items():
            if isinstance(value, str) and len(value) > 10:
                return value
        return None


# Global import service instance
import_service = ImportService()
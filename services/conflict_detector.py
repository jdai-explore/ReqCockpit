"""
Conflict detection service for ReqCockpit
Identifies and flags supplier disagreements on requirements
"""
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

from models.base import db_manager
from models.project import Project
from models.requirement import MasterRequirement, SupplierFeedback
from config import NormalizedStatus

logger = logging.getLogger(__name__)


class ConflictDetector:
    """
    Service for detecting conflicts in supplier feedback
    
    Identifies when suppliers provide conflicting feedback on the same requirement,
    such as different status values or contradictory comments.
    """
    
    @staticmethod
    def detect_status_conflicts(requirement_id: int) -> Dict[str, Any]:
        """
        Detect status conflicts for a specific requirement
        
        Args:
            requirement_id: ID of the MasterRequirement
            
        Returns:
            Dictionary with conflict information
        """
        session = db_manager.get_session()
        if not session:
            return {'has_conflict': False, 'conflicting_suppliers': []}
        
        try:
            # Get all feedback for this requirement
            feedbacks = session.query(SupplierFeedback).filter(
                SupplierFeedback.requirement_id == requirement_id
            ).all()
            
            if len(feedbacks) < 2:
                return {'has_conflict': False, 'conflicting_suppliers': []}
            
            # Group by normalized status
            status_groups = defaultdict(list)
            for feedback in feedbacks:
                status_groups[feedback.normalized_status].append(
                    feedback.supplier.name
                )
            
            # Check if there are conflicting statuses
            # Conflict = multiple different statuses present
            if len(status_groups) > 1:
                # Filter out NOT_SET status from conflict detection
                non_null_statuses = {
                    status: suppliers 
                    for status, suppliers in status_groups.items()
                    if status != NormalizedStatus.NOT_SET.value
                }
                
                if len(non_null_statuses) > 1:
                    return {
                        'has_conflict': True,
                        'conflicting_suppliers': [
                            supplier for suppliers in non_null_statuses.values()
                            for supplier in suppliers
                        ],
                        'status_distribution': {
                            status: len(suppliers)
                            for status, suppliers in non_null_statuses.items()
                        }
                    }
            
            return {'has_conflict': False, 'conflicting_suppliers': []}
        
        finally:
            session.close()
    
    @staticmethod
    def detect_all_conflicts(project_id: int) -> Dict[int, Dict[str, Any]]:
        """
        Detect all conflicts in a project
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary mapping requirement_id to conflict info
        """
        session = db_manager.get_session()
        if not session:
            return {}
        
        try:
            # Get all requirements in project
            requirements = session.query(MasterRequirement).filter(
                MasterRequirement.project_id == project_id
            ).all()
            
            conflicts = {}
            for req in requirements:
                conflict_info = ConflictDetector.detect_status_conflicts(req.id)
                if conflict_info['has_conflict']:
                    conflicts[req.id] = conflict_info
            
            return conflicts
        
        finally:
            session.close()
    
    @staticmethod
    def get_conflict_summary(project_id: int) -> Dict[str, Any]:
        """
        Get a summary of conflicts in a project
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary with conflict statistics
        """
        conflicts = ConflictDetector.detect_all_conflicts(project_id)
        
        total_requirements = 0
        conflicted_requirements = len(conflicts)
        conflicting_suppliers = set()
        
        session = db_manager.get_session()
        if session:
            try:
                total_requirements = session.query(MasterRequirement).filter(
                    MasterRequirement.project_id == project_id
                ).count()
                
                for conflict_info in conflicts.values():
                    conflicting_suppliers.update(conflict_info['conflicting_suppliers'])
            finally:
                session.close()
        
        return {
            'total_requirements': total_requirements,
            'conflicted_requirements': conflicted_requirements,
            'conflict_percentage': (
                (conflicted_requirements / total_requirements * 100)
                if total_requirements > 0 else 0
            ),
            'unique_suppliers_in_conflicts': len(conflicting_suppliers),
            'conflicts_by_requirement': conflicts
        }


# Global instance
conflict_detector = ConflictDetector()

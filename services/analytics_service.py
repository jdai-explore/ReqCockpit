"""
Analytics service for ReqCockpit
Provides dashboard metrics and KPI calculations
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from models.base import db_manager
from models.project import Project
from models.iteration import Iteration
from models.supplier import Supplier
from models.requirement import MasterRequirement
from models.feedback import SupplierFeedback
from models.decision import CustREDecision
from config import NormalizedStatus, DecisionStatus

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for calculating dashboard metrics and KPIs
    
    Provides aggregated statistics for project overview, supplier performance,
    and decision tracking.
    """
    
    @staticmethod
    def get_project_overview(project_id: int) -> Dict[str, Any]:
        """
        Get high-level project statistics
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary with project overview metrics
        """
        session = db_manager.get_session()
        if not session:
            return {}
        
        try:
            project = session.query(Project).filter(
                Project.id == project_id
            ).first()
            
            if not project:
                return {}
            
            # Count requirements
            total_requirements = session.query(MasterRequirement).filter(
                MasterRequirement.project_id == project_id
            ).count()
            
            # Count suppliers
            total_suppliers = session.query(Supplier).filter(
                Supplier.project_id == project_id
            ).count()
            
            # Count iterations
            total_iterations = session.query(Iteration).filter(
                Iteration.project_id == project_id
            ).count()
            
            # Count decisions
            total_decisions = session.query(CustREDecision).join(
                MasterRequirement
            ).filter(
                MasterRequirement.project_id == project_id
            ).count()
            
            return {
                'project_name': project.name,
                'total_requirements': total_requirements,
                'total_suppliers': total_suppliers,
                'total_iterations': total_iterations,
                'total_decisions': total_decisions,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'last_modified': project.last_modified.isoformat() if project.last_modified else None
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_status_distribution(project_id: int) -> Dict[str, int]:
        """
        Get distribution of normalized statuses across all feedback
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary mapping status to count
        """
        session = db_manager.get_session()
        if not session:
            return {}
        
        try:
            # Get all feedback for project
            feedbacks = session.query(SupplierFeedback).join(
                MasterRequirement
            ).filter(
                MasterRequirement.project_id == project_id
            ).all()
            
            distribution = defaultdict(int)
            for feedback in feedbacks:
                distribution[feedback.normalized_status] += 1
            
            return dict(distribution)
        
        finally:
            session.close()
    
    @staticmethod
    def get_supplier_performance(project_id: int) -> List[Dict[str, Any]]:
        """
        Get performance metrics for each supplier
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of supplier performance dictionaries
        """
        session = db_manager.get_session()
        if not session:
            return []
        
        try:
            suppliers = session.query(Supplier).filter(
                Supplier.project_id == project_id
            ).all()
            
            performance_list = []
            
            for supplier in suppliers:
                # Count feedback entries
                feedback_count = session.query(SupplierFeedback).filter(
                    SupplierFeedback.supplier_id == supplier.id
                ).count()
                
                # Count by status
                status_counts = defaultdict(int)
                feedbacks = session.query(SupplierFeedback).filter(
                    SupplierFeedback.supplier_id == supplier.id
                ).all()
                
                for feedback in feedbacks:
                    status_counts[feedback.normalized_status] += 1
                
                # Calculate acceptance rate
                accepted_count = status_counts.get(NormalizedStatus.ACCEPTED.value, 0)
                acceptance_rate = (
                    (accepted_count / feedback_count * 100)
                    if feedback_count > 0 else 0
                )
                
                performance_list.append({
                    'supplier_name': supplier.name,
                    'supplier_id': supplier.id,
                    'feedback_count': feedback_count,
                    'acceptance_rate': round(acceptance_rate, 2),
                    'status_distribution': dict(status_counts),
                    'last_feedback': max(
                        (f.created_at for f in feedbacks),
                        default=None
                    ).isoformat() if feedbacks else None
                })
            
            # Sort by acceptance rate descending
            performance_list.sort(key=lambda x: x['acceptance_rate'], reverse=True)
            
            return performance_list
        
        finally:
            session.close()
    
    @staticmethod
    def get_decision_summary(project_id: int) -> Dict[str, Any]:
        """
        Get summary of CustRE decisions
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary with decision statistics
        """
        session = db_manager.get_session()
        if not session:
            return {}
        
        try:
            decisions = session.query(CustREDecision).join(
                MasterRequirement
            ).filter(
                MasterRequirement.project_id == project_id
            ).all()
            
            decision_counts = defaultdict(int)
            total_decisions = len(decisions)
            
            for decision in decisions:
                decision_counts[decision.decision_status] += 1
            
            return {
                'total_decisions': total_decisions,
                'by_status': dict(decision_counts),
                'decision_rate': (
                    (total_decisions / session.query(MasterRequirement).filter(
                        MasterRequirement.project_id == project_id
                    ).count() * 100)
                    if session.query(MasterRequirement).filter(
                        MasterRequirement.project_id == project_id
                    ).count() > 0 else 0
                )
            }
        
        finally:
            session.close()
    
    @staticmethod
    def get_iteration_timeline(project_id: int) -> List[Dict[str, Any]]:
        """
        Get timeline of iterations with feedback counts
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of iteration timeline entries
        """
        session = db_manager.get_session()
        if not session:
            return []
        
        try:
            iterations = session.query(Iteration).filter(
                Iteration.project_id == project_id
            ).order_by(Iteration.created_at).all()
            
            timeline = []
            for iteration in iterations:
                # Count feedback in this iteration
                feedback_count = session.query(SupplierFeedback).filter(
                    SupplierFeedback.iteration_id == iteration.id
                ).count()
                
                timeline.append({
                    'iteration_name': iteration.name,
                    'iteration_id': iteration.id,
                    'created_at': iteration.created_at.isoformat() if iteration.created_at else None,
                    'feedback_count': feedback_count,
                    'supplier_count': len(set(
                        f.supplier_id for f in session.query(SupplierFeedback).filter(
                            SupplierFeedback.iteration_id == iteration.id
                        ).all()
                    ))
                })
            
            return timeline
        
        finally:
            session.close()
    
    @staticmethod
    def get_dashboard_data(project_id: int) -> Dict[str, Any]:
        """
        Get complete dashboard data in one call
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary with all dashboard metrics
        """
        return {
            'overview': AnalyticsService.get_project_overview(project_id),
            'status_distribution': AnalyticsService.get_status_distribution(project_id),
            'supplier_performance': AnalyticsService.get_supplier_performance(project_id),
            'decision_summary': AnalyticsService.get_decision_summary(project_id),
            'iteration_timeline': AnalyticsService.get_iteration_timeline(project_id)
        }


# Global instance
analytics_service = AnalyticsService()

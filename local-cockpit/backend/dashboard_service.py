from sqlalchemy.orm import sessionmaker
from .database.schema import MasterRequirement, SupplierFeedback, Iteration
from collections import Counter

class DashboardService:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_dashboard_metrics(self, project_id, iteration_id):
        session = self.Session()

        iteration = session.query(Iteration).filter_by(project_id=project_id, id=iteration_id).first()
        if not iteration:
            return {}

        total_requirements = session.query(MasterRequirement).filter_by(project_id=project_id).count()

        feedback = (
            session.query(SupplierFeedback)
            .filter(SupplierFeedback.iteration_id == iteration.id)
            .all()
        )

        status_counts = Counter(f.supplier_status_normalized for f in feedback)

        session.close()

        return {
            "total_requirements": total_requirements,
            "accepted_count": status_counts.get("Accepted", 0),
            "clarification_needed_count": status_counts.get("Clarification Needed", 0),
            "rejected_count": status_counts.get("Rejected", 0),
            # "conflicts_detected": a more complex query would be needed here, or it could be calculated on the frontend
        }

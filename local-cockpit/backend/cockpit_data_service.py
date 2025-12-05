from sqlalchemy.orm import sessionmaker, joinedload
from .database.schema import MasterRequirement, SupplierFeedback, Supplier, Iteration

class CockpitDataService:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_cockpit_data(self, project_id, iteration_id):
        session = self.Session()

        iteration = session.query(Iteration).filter_by(project_id=project_id, id=iteration_id).first()
        if not iteration:
            return []

        requirements = (
            session.query(MasterRequirement)
            .filter(MasterRequirement.project_id == project_id)
            .options(
                joinedload(MasterRequirement.supplier_feedback)
                .joinedload(SupplierFeedback.supplier)
            )
            .all()
        )

        cockpit_data = []
        for req in requirements:
            suppliers_feedback = {}
            for feedback in req.supplier_feedback:
                if feedback.iteration_id == iteration.id:
                    suppliers_feedback[feedback.supplier.name] = {
                        "status": feedback.supplier_status,
                        "normalized_status": feedback.supplier_status_normalized,
                        "comment": feedback.supplier_comment,
                    }

            cockpit_data.append({
                "id": req.id,
                "reqif_id": req.reqif_id,
                "text": req.text_content,
                "suppliers": suppliers_feedback,
            })

        session.close()
        return cockpit_data

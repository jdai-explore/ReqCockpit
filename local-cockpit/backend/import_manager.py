import os
from sqlalchemy.orm import sessionmaker
from .database.schema import MasterRequirement, Supplier, Iteration, SupplierFeedback
from .reqif_parser import ReqIFParser

class ImportManager:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def import_master_spec(self, project_id, file_path):
        parser = ReqIFParser()
        requirements_data = parser.parse_file(file_path)

        session = self.Session()

        for req_data in requirements_data:
            new_req = MasterRequirement(
                project_id=project_id,
                reqif_id=req_data.get('identifier') or req_data.get('id'),
                text_content=req_data.get('attributes', {}).get('ReqIF.Text'),
                raw_attributes=req_data.get('raw_attributes')
            )
            session.add(new_req)

        session.commit()
        session.close()

        return len(requirements_data)

    def import_supplier_feedback(self, project_id, iteration_id_str, supplier_name, file_path):
        parser = ReqIFParser()
        feedback_data = parser.parse_file(file_path)

        session = self.Session()

        # Get or create supplier
        supplier = session.query(Supplier).filter_by(project_id=project_id, name=supplier_name).first()
        if not supplier:
            supplier = Supplier(project_id=project_id, name=supplier_name)
            session.add(supplier)
            session.commit()

        # Get iteration
        iteration = session.query(Iteration).filter_by(project_id=project_id, iteration_id=iteration_id_str).first()
        if not iteration:
            iteration = Iteration(project_id=project_id, iteration_id=iteration_id_str)
            session.add(iteration)
            session.commit()

        matched_count = 0
        for data in feedback_data:
            reqif_id = data.get('identifier') or data.get('id')
            master_req = session.query(MasterRequirement).filter_by(project_id=project_id, reqif_id=reqif_id).first()

            if master_req:
                feedback = SupplierFeedback(
                    master_req_id=master_req.id,
                    iteration_id=iteration.id,
                    supplier_id=supplier.id,
                    supplier_status=data.get('attributes', {}).get('ReqIF-WF.SupplierStatus'),
                    supplier_comment=data.get('attributes', {}).get('ReqIF-WF.SupplierComment'),
                    raw_attributes=data.get('raw_attributes')
                )
                session.add(feedback)
                matched_count += 1

        session.commit()
        session.close()

        return matched_count

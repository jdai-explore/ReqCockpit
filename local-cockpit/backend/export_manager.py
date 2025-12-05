import pandas as pd
from sqlalchemy.orm import sessionmaker
from .database.schema import MasterRequirement, SupplierFeedback, CustREDecision, Supplier, Iteration

class ExportManager:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def export_to_csv(self, project_id, iteration_id, output_path):
        data = self._get_export_data(project_id, iteration_id)
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)

    def export_to_xlsx(self, project_id, iteration_id, output_path):
        data = self._get_export_data(project_id, iteration_id)
        df = pd.DataFrame(data)

        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Requirements')

            # Auto-adjust column widths
            for column in df:
                column_width = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                writer.sheets['Requirements'].set_column(col_idx, col_idx, column_width)

    def _get_export_data(self, project_id, iteration_id):
        session = self.Session()

        # This is a simplified query. A more complex query might be needed to get all the data in one go.
        # For now, we'll build it up step by step.

        requirements = session.query(MasterRequirement).filter_by(project_id=project_id).all()

        export_data = []
        for req in requirements:
            row = {
                'ReqIF ID': req.reqif_id,
                'Master Text': req.text_content
            }

            feedback = (
                session.query(SupplierFeedback)
                .join(Supplier)
                .filter(SupplierFeedback.master_req_id == req.id, SupplierFeedback.iteration_id == iteration_id)
                .all()
            )

            for f in feedback:
                row[f'{f.supplier.name} Status'] = f.supplier_status
                row[f'{f.supplier.name} Comment'] = f.supplier_comment

            decision = (
                session.query(CustREDecision)
                .filter_by(master_req_id=req.id, iteration_id=iteration_id)
                .first()
            )

            if decision:
                row['CustRE Decision'] = decision.decision_status
                row['Action Note'] = decision.action_note

            export_data.append(row)

        session.close()
        return export_data

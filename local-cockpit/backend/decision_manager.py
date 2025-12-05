from sqlalchemy.orm import sessionmaker
from .database.schema import CustREDecision

class DecisionManager:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def save_decision(self, master_req_id, iteration_id, status, note, user):
        session = self.Session()

        decision = (
            session.query(CustREDecision)
            .filter_by(master_req_id=master_req_id, iteration_id=iteration_id)
            .first()
        )

        if decision:
            decision.decision_status = status
            decision.action_note = note
            decision.decided_by = user
        else:
            decision = CustREDecision(
                master_req_id=master_req_id,
                iteration_id=iteration_id,
                decision_status=status,
                action_note=note,
                decided_by=user,
            )
            session.add(decision)

        session.commit()
        session.close()

    def get_decision_history(self, master_req_id):
        session = self.Session()

        history = (
            session.query(CustREDecision)
            .filter_by(master_req_id=master_req_id)
            .order_by(CustREDecision.decided_at.desc())
            .all()
        )

        session.close()
        return [
            {
                "iteration_id": item.iteration_id,
                "status": item.decision_status,
                "note": item.action_note,
                "user": item.decided_by,
                "date": item.decided_at.isoformat(),
            }
            for item in history
        ]

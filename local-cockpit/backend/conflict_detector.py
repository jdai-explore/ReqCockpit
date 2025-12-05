
class ConflictDetector:
    def detect_conflicts(self, cockpit_data):
        conflict_ids = []
        for req in cockpit_data:
            statuses = set()
            for supplier_feedback in req['suppliers'].values():
                normalized_status = supplier_feedback.get('normalized_status')
                if normalized_status in ['Clarification Needed', 'Rejected']:
                    statuses.add(normalized_status)

            if len(statuses) > 1:
                conflict_ids.append(req['id'])

        return conflict_ids

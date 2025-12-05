
DEFAULT_STATUS_MAPPINGS = {
    "ok": "Accepted",
    "compliant": "Accepted",
    "accepted": "Accepted",
    "agreed": "Accepted",
    "needs clarification": "Clarification Needed",
    "tobeclarified": "Clarification Needed",
    "not accepted": "Rejected",
    "notagreed": "Rejected",
    "rejected": "Rejected",
}

class StatusHarmonizer:
    def __init__(self, custom_mappings=None):
        self.mappings = DEFAULT_STATUS_MAPPINGS.copy()
        if custom_mappings:
            self.mappings.update({k.lower().strip(): v for k, v in custom_mappings.items()})

    def normalize_status(self, original_status):
        if not original_status:
            return "Unknown"

        normalized = self.mappings.get(original_status.lower().strip().replace(" ", ""))
        return normalized if normalized else "Unknown"

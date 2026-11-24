import secrets, json
from datetime import datetime, timezone

class ClickSimulator:
    """Consent-based harmless lab landing-page event tracker."""
    def __init__(self, db, base_url): self.db, self.base_url = db, base_url.rstrip("/")
    def create(self, label="Training simulation"):
        sim_id=secrets.token_urlsafe(12); now=datetime.now(timezone.utc).isoformat()
        self.db.create_simulation(sim_id, label[:100], now)
        self.db.event(sim_id,"created",now,json.dumps({"note":"No exploit or payload is used"}))
        return {"id":sim_id,"url":f"{self.base_url}/lab/{sim_id}"}
    def record(self, sim_id, event_type, details=None):
        if event_type not in {"landing_view","consent_click","simulation_complete"}: raise ValueError("Unsupported event")
        now=datetime.now(timezone.utc).isoformat()
        self.db.event(sim_id,event_type,now,json.dumps(details or {},separators=(",",":")))
        return {"simulation_id":sim_id,"event":event_type,"timestamp":now}

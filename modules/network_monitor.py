from urllib.parse import urlparse
from datetime import datetime, timezone
class NetworkMonitor:
    """Manual event logger for lab traffic; no packet sniffing or MITM."""
    def __init__(self, db): self.db=db
    def record(self, method, url, status=None, note=""):
        if method not in {"GET","POST","PUT","DELETE","HEAD","OPTIONS"}: raise ValueError("Invalid HTTP method")
        p=urlparse(url)
        if p.scheme not in {"http","https"} or not p.hostname: raise ValueError("URL must be HTTP(S)")
        self.db.log_network_event(datetime.now(timezone.utc).isoformat(),method,url,int(status) if status is not None else None,note[:500])
        return {"logged":True,"method":method,"host":p.hostname,"status":status}

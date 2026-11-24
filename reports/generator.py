from pathlib import Path
import json, html
from datetime import datetime, timezone
class ReportGenerator:
    def __init__(self, outdir="output"):
        self.out=Path(outdir); self.out.mkdir(parents=True,exist_ok=True)
    def json_report(self, name, data):
        p=self.out/(self._safe(name)+".json"); p.write_text(json.dumps(data,indent=2,ensure_ascii=False)); return str(p)
    def html_report(self, name, data):
        title=html.escape(name); content=html.escape(json.dumps(data,indent=2,ensure_ascii=False))
        p=self.out/(self._safe(name)+".html")
        p.write_text(f'''<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>body{{font-family:system-ui;margin:2rem;background:#f5f7fa;color:#17212b}}pre{{background:white;padding:1rem;border-radius:8px;overflow:auto}}</style></head><body><h1>{title}</h1><p>Generated {datetime.now(timezone.utc).isoformat()}</p><pre>{content}</pre></body></html>''')
        return str(p)
    @staticmethod
    def _safe(name): return "".join(c for c in name if c.isalnum() or c in "-_ ").strip().replace(" ","_")[:80] or "report"

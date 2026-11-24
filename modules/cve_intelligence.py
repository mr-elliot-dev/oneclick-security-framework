import requests
from datetime import datetime, timezone

NVD="https://services.nvd.nist.gov/rest/json/cves/2.0"
class CVEIntelligence:
    def __init__(self, api_key="", timeout=12): self.api_key,self.timeout=api_key,timeout
    def search(self, keyword, limit=10):
        if not isinstance(keyword,str) or not keyword.strip() or len(keyword)>100: raise ValueError("Keyword required (max 100 chars)")
        limit=max(1,min(int(limit),20)); headers={"User-Agent":"LabMobileSecurityFramework/1.0"}
        if self.api_key: headers["apiKey"]=self.api_key
        try:
            r=requests.get(NVD,params={"keywordSearch":keyword.strip(),"resultsPerPage":limit},headers=headers,timeout=self.timeout)
            r.raise_for_status(); data=r.json(); items=[]
            for item in data.get("vulnerabilities",[]):
                cve=item.get("cve",{}); metrics=cve.get("metrics",{}); cvss=None
                for key in ("cvssMetricV31","cvssMetricV30","cvssMetricV2"):
                    if metrics.get(key):
                        cvss=metrics[key][0].get("cvssData",{}).get("baseScore"); break
                desc=next((d.get("value","") for d in cve.get("descriptions",[]) if d.get("lang")=="en"),"")
                refs=[x.get("url") for x in cve.get("references",[])[:8]]
                items.append({"id":cve.get("id"),"cvss":cvss,"description":desc,"references":refs,"published":cve.get("published"),"version_match":"keyword result only; affected-version ranges not evaluated","status":"potential match; verify affected products and versions"})
            return {"query":keyword,"retrieved_at":datetime.now(timezone.utc).isoformat(),"count":len(items),"items":items}
        except requests.RequestException as e: return {"error":f"NVD request failed: {e}"}

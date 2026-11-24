import argparse, json, uuid
from core.config import load_config
from core.database import Database
from modules.url_analyzer import URLAnalyzer
from modules.click_simulator import ClickSimulator
from modules.android_auditor import AndroidAuditor
from modules.cve_intelligence import CVEIntelligence
from modules.network_monitor import NetworkMonitor
from reports.generator import ReportGenerator

def main():
    cfg=load_config(); db=Database(cfg["database"]); reports=ReportGenerator()
    p=argparse.ArgumentParser(prog="ocsrf",description="One-click Security Research Framework (safe lab simulator)")
    sub=p.add_subparsers(dest="command",required=True)
    u=sub.add_parser("url",help="Analyze a URL (optional bounded fetch)"); u.add_argument("target"); u.add_argument("--fetch",action="store_true")
    sub.add_parser("android",help="Read Android properties via authorized ADB")
    c=sub.add_parser("cve",help="Search NVD by product keyword"); c.add_argument("keyword"); c.add_argument("--limit",type=int,default=10)
    s=sub.add_parser("simulate",help="Create consent-based lab link"); s.add_argument("--label",default="Training simulation")
    n=sub.add_parser("network-log",help="Manually log a lab HTTP event"); n.add_argument("method"); n.add_argument("url"); n.add_argument("--status",type=int); n.add_argument("--note",default="")
    sub.add_parser("simulations",help="List simulations")
    args=p.parse_args()
    if args.command=="url": result=URLAnalyzer(cfg["request_timeout"],cfg["max_fetch_bytes"]).analyze(args.target,args.fetch)
    elif args.command=="android": result=AndroidAuditor().assess()
    elif args.command=="cve": result=CVEIntelligence(cfg["nvd_api_key"]).search(args.keyword,args.limit)
    elif args.command=="simulate": result=ClickSimulator(db,cfg["lab_base_url"]).create(args.label)
    elif args.command=="network-log": result=NetworkMonitor(db).record(args.method.upper(),args.url,args.status,args.note)
    else: result=db.all_simulations()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if args.command not in {"simulate","simulations"}:
        name=f"{args.command}-{uuid.uuid4().hex[:8]}"; reports.json_report(name,result); reports.html_report(name,result)
if __name__=="__main__": main()

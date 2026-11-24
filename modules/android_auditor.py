import subprocess, re

class AndroidAuditor:
    SAFE_PROPERTIES={"release":"ro.build.version.release","sdk":"ro.build.version.sdk","patch":"ro.build.version.security_patch","manufacturer":"ro.product.manufacturer","model":"ro.product.model"}
    def __init__(self, adb="adb", timeout=8): self.adb,self.timeout=adb,timeout
    def _run(self, args):
        try:
            p=subprocess.run([self.adb,*args],capture_output=True,text=True,timeout=self.timeout)
            if p.returncode: return {"error":p.stderr.strip() or "ADB command failed"}
            return {"output":p.stdout.strip()}
        except FileNotFoundError: return {"error":"ADB is not installed or not in PATH"}
        except subprocess.TimeoutExpired: return {"error":"ADB command timed out"}
    def assess(self):
        devices=self._run(["devices"])
        if "output" not in devices: return {"error":devices["error"]}
        lines=devices["output"].splitlines()[1:]
        active=[x.split()[0] for x in lines if len(x.split())>=2 and x.split()[1]=="device"]
        if not active: return {"error":"No authorized ADB device found. Enable USB debugging and approve this host."}
        serial=active[0]; facts={"serial":"redacted","connected_device_count":len(active)}
        for k,prop in self.SAFE_PROPERTIES.items():
            out=self._run(["-s",serial,"shell","getprop",prop]); facts[k]=out.get("output",out.get("error"))
        browser_packages={"Chrome":"com.android.chrome","Android System WebView":"com.google.android.webview","Firefox":"org.mozilla.firefox"}
        facts["browser_versions"]={}
        for name,pkg in browser_packages.items():
            out=self._run(["-s",serial,"shell","dumpsys","package",pkg])
            text=out.get("output","")
            m=re.search(r"versionName=([^\s]+)",text)
            facts["browser_versions"][name]=m.group(1) if m else ("not installed" if "error" not in out else "unavailable")
        checks=[]
        if facts.get("patch") and facts["patch"] != "": checks.append({"check":"security_patch_level","status":"present","value":facts["patch"]})
        else: checks.append({"check":"security_patch_level","status":"unknown","recommendation":"Check Android Settings > Security"})
        facts["checks"]=checks
        facts["limitations"]=["ADB reports device properties only; it does not prove exploitability.","Browser patch status requires vendor-specific comparison.","Device serial is not stored or returned."]
        return facts

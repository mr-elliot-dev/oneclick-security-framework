from urllib.parse import urlparse
import socket, ssl, ipaddress, re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup


class URLAnalyzer:
    SUSPICIOUS_WORDS = ("login", "verify", "secure", "account", "update", "password", "wallet", "signin")
    def __init__(self, timeout=5, max_bytes=512_000):
        self.timeout, self.max_bytes = timeout, max_bytes


    def _validate_url(self, url):
        if not isinstance(url, str) or len(url) > 2048: raise ValueError("URL must be a string under 2048 characters")
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.hostname: raise ValueError("Only HTTP/HTTPS URLs are supported")
        if p.username or p.password: raise ValueError("URLs containing embedded credentials are not allowed")
        return p


    def _public_host(self, host):
        try:
            addresses = {x[4][0] for x in socket.getaddrinfo(host, None)}
        except socket.gaierror as e: raise ValueError(f"DNS lookup failed: {e}")
        if not addresses: raise ValueError("Host did not resolve")
        for addr in addresses:
            ip = ipaddress.ip_address(addr)
            if not ip.is_global: raise ValueError("Refusing to connect to private, loopback, link-local, or reserved IPs")
        return sorted(addresses)

    def analyze(self, url, fetch=False):
        parsed = self._validate_url(url)
        host = parsed.hostname.lower()
        indicators, info = [], []
        if parsed.scheme != "https": indicators.append({"name":"unencrypted_http","weight":25,"description":"URL does not use HTTPS"})
        if len(host.split(".")) > 4: indicators.append({"name":"deep_subdomain","weight":10,"description":"Unusually deep subdomain structure"})
        if "xn--" in host: indicators.append({"name":"punycode","weight":20,"description":"Internationalized/punycode hostname; check for lookalikes"})
        if re.search(r"\d{1,3}(?:\.\d{1,3}){3}$", host): indicators.append({"name":"ip_host","weight":15,"description":"URL uses an IP address instead of a domain"})
        if any(w in (host + parsed.path).lower() for w in self.SUSPICIOUS_WORDS): indicators.append({"name":"credential_terms","weight":15,"description":"Login/verification-related terms in hostname or path"})
        if len(url) > 150: indicators.append({"name":"long_url","weight":5,"description":"Long URL may obscure destination"})
        if parsed.hostname.count("-") >= 3: indicators.append({"name":"hyphenated_host","weight":5,"description":"Hostname contains multiple hyphens"})
        result = {"url":url,"host":host,"scheme":parsed.scheme,"indicators":indicators,"score":min(100,sum(x["weight"] for x in indicators)),"checked_at":datetime.now(timezone.utc).isoformat(),"dns":None,"tls":None,"fetch":None}
        try: result["dns"] = self._public_host(host)
        except ValueError as e: result["dns"] = {"error":str(e)}
        if parsed.scheme == "https":
            try:
                ctx=ssl.create_default_context()
                with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                    s.settimeout(self.timeout); s.connect((host,parsed.port or 443)); cert=s.getpeercert()
                result["tls"]={"verified":True,"subject":cert.get("subject"),"issuer":cert.get("issuer"),"expires":cert.get("notAfter")}
            except Exception as e: result["tls"]={"verified":False,"error":str(e)}
        if fetch:
            result["fetch"] = self._fetch(url)
        return result

    def _fetch(self, url):
        # Redirects are inspected but not followed; protects against redirect chains and SSRF.
        try:
            p=self._validate_url(url); self._public_host(p.hostname)
            r=requests.get(url, timeout=self.timeout, allow_redirects=False, stream=True,
                         headers={"User-Agent":"LabSecurityAnalyzer/1.0"})
            snippet=b""
            for chunk in r.iter_content(8192):
                snippet += chunk
                if len(snippet)>=self.max_bytes: snippet=snippet[:self.max_bytes]; break
            soup=BeautifulSoup(snippet, "html.parser")
            links=[x.get("href") for x in soup.find_all("a",href=True)[:30]]
            return {"status":r.status_code,"headers":{"content_type":r.headers.get("Content-Type"),"server":r.headers.get("Server")},"redirect_location":r.headers.get("Location"),"links_sample":links,"bytes_sampled":len(snippet)}
        except Exception as e: return {"error":str(e)}

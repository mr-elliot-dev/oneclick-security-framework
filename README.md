# One-Click Security Research Framework (OCSRF)

A defensive, consent-based lab toolkit for URL triage, Android property assessment over ADB, keyword CVE lookup, click-chain simulation, manual network-event logging, and JSON/HTML reports. **It does not exploit vulnerabilities, install payloads, capture packet contents, or collect visitor IP addresses/user agents.**

## Current implementation / honest limitations

- **URL analysis:** heuristic indicators; HTTPS certificate verification via Python TLS; DNS lookup; optional bounded HTML sampling. HTTP fetch does not follow redirects and refuses hosts resolving to non-public IPs. This is a triage aid, not a verdict. URL fetch is best run in an isolated lab because DNS can change between validation and connection.
- **Click simulation:** unique token URL and server-side landing/click/complete events. Consent click is the only simulated action. No exploit or payload.
- **Android assessment:** reads Android release, SDK, security patch, manufacturer/model, and installed Chrome/WebView/Firefox package versions from an authorized ADB device. Serial is redacted. It does not claim to validate patch status against OEM bulletins.
- **CVE:** NVD 2.0 keyword search, CVSS score, description, references. **Affected-version range matching is not implemented**; results are labeled potential matches.
- **Network monitor:** manual HTTP event logger only; no packet sniffing, proxy interception, or MITM.
- **Reports:** JSON and HTML reports. HTML output escapes report contents.

## Kali Linux installation

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip adb
cd oneclick-security-framework
./install.sh
source .venv/bin/activate
pytest -q
```

## Run

```bash
# URL triage; fetch is optional and bounded/no-follow
python cli.py url https://example.org
python cli.py url https://example.org --fetch

# Android assessment: connect/authorize the lab device first
adb devices
python cli.py android

# NVD keyword lookup
python cli.py cve "Android Chrome" --limit 8

# Create a click-simulation URL; use only in your controlled lab
python cli.py simulate --label "Android browser awareness test"

# Manually record a lab traffic event
python cli.py network-log GET https://example.org --status 200 --note "Test browsing event"

# List stored simulations
python cli.py simulations

# Web dashboard/landing server (loopback by default)
python app.py
# Open http://127.0.0.1:5000
```

Generated JSON/HTML reports are stored under `output/`. SQLite data is stored in `data/framework.db`.

## Android 13 lab setup

1. Use a dedicated Android 13 test device and a test-only Google/browser account (prefer no account at all).
2. Enable Developer options, then USB debugging; connect USB and accept the ADB authorization prompt.
3. Confirm `adb devices` shows the device as `device`, not `unauthorized`.
4. Run `python cli.py android`. Results contain device build properties, patch date, and browser package versions; check vendor security bulletins separately.
5. Create a simulation using `python cli.py simulate`. For a phone on the same Wi-Fi, set `lab_base_url` in `config.yaml` to the host's lab IP and configure Flask to bind to that LAN IP **only on a trusted isolated lab network**. The simulator stores no visitor IP or browser fingerprint.
6. Open the simulation link on the test device. The page explains the training purpose; tap **Continue simulation** to log consent and completion. View the event in SQLite/report output.


## Tests

Run `pytest -q`. Tests cover URL input validation and indicator scoring, simulation persistence, and report generation. Network-dependent NVD and Android-device integration checks are not run automatically.


## Safety and deployment

- Keep the web service bound to localhost unless you deliberately use an isolated lab network.
- Do not expose this development Flask server to the Internet. Use a production WSGI server and security review before any wider deployment.
- Only scan systems and devices for which you have explicit permission.
- Do not add real payloads, exploit delivery, covert tracking, or personal data collection to this framework.

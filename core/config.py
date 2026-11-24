from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {
    "host": "127.0.0.1", "port": 5000, "database": "data/framework.db",
    "log_file": "logs/framework.log", "lab_base_url": "http://127.0.0.1:5000",
    "nvd_api_key": "", "request_timeout": 5, "max_fetch_bytes": 512000,
}

def load_config(path="config.yaml"):
    cfg = DEFAULTS.copy()
    p = Path(path)
    if p.exists():
        loaded = yaml.safe_load(p.read_text()) or {}
        if not isinstance(loaded, dict):
            raise ValueError("Configuration must be a YAML mapping")
        cfg.update(loaded)
    for key in ("host", "lab_base_url", "database", "log_file"):
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            raise ValueError(f"Invalid config value: {key}")
    cfg["port"] = int(cfg["port"])
    cfg["request_timeout"] = max(1, min(int(cfg["request_timeout"]), 15))
    cfg["max_fetch_bytes"] = max(1024, min(int(cfg["max_fetch_bytes"]), 2_000_000))
    return cfg

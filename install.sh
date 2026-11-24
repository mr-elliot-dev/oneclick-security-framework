#!/usr/bin/env bash
set -euo pipefail
python3 --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
mkdir -p data logs output
chmod +x cli.py
printf '\nInstall complete. Activate: source .venv/bin/activate\n'
printf 'Run web: python app.py\nCLI: python cli.py --help\n'

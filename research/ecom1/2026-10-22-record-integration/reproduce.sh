#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 build.py
uv run --offline --with python-minifier==3.4.0 python pack5h.py --check record_agent.py record_readable.py
uv run --offline --with pydantic-monty==1.2.0 python verify.py
uv run --offline --with pydantic-monty==1.2.0 python verify_audit.py
python3 verify_integration.py

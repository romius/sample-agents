#!/bin/sh
set -eu
cd "$(dirname "$0")"
(cd ../2026-10-22-record-integration && python3 build.py)
python3 ../2026-10-22-receipt-header-review/build.py
python3 ../2026-10-22-clarification-review/review.py
python3 build.py
uv run --python 3.14 --no-project --with pydantic-monty==1.2.0 python verify.py
uv run --python 3.14 --no-project --with pydantic-monty==1.2.0 python full_agent_verify.py

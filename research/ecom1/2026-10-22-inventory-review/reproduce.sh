#!/bin/sh
set -eu
cd "$(dirname "$0")"
uv run --python 3.14 --no-project --with pydantic-monty==1.2.0 python review.py
uv run --python 3.14 --no-project --with python-minifier==3.4.0 python packing_probe.py
uv run --python 3.14 --no-project --with python-minifier==3.4.0 python packing_variants.py
python3 longest_probe.py
uv run --python 3.14 --no-project --with pydantic-monty==1.2.0 python verify_packing.py

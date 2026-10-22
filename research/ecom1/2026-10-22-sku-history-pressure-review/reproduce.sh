#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd /tmp
export UV_CACHE_DIR=/tmp/ecom1-uv-cache
export PYTHONWARNINGS=ignore::SyntaxWarning
uv run --python 3.14 --no-project --offline --with python-minifier==3.4.0 python "$here/build.py"
uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python "$here/check.py"
uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python "$here/verify_regressions.py"

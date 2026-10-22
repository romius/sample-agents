#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd /tmp
export UV_CACHE_DIR=/tmp/ecom1-uv-cache
export PYTHONWARNINGS=ignore::SyntaxWarning
uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 --with python-minifier==3.4.0 python "$here/build.py"
uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 --with python-minifier==3.4.0 python "$here/verify_codec.py"
uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 --with python-minifier==3.4.0 python "$here/verify_whole_agent.py"
uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 --with python-minifier==3.4.0 python "$here/probe_literal_limits.py"

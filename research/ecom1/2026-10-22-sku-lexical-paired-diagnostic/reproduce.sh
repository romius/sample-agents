#!/bin/sh
set -eu
cd "$(dirname "$0")"
ECOM_DIAG_PYTHON=${ECOM_DIAG_PYTHON:-python3}
"$ECOM_DIAG_PYTHON" build.py
"$ECOM_DIAG_PYTHON" verify.py

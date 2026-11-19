#!/bin/bash
set -euo pipefail

export PATH="$TMT_TREE/.venv/bin:$PATH"
cd "$TMT_TREE/tests"
PYTHON=python3 ./testsuite

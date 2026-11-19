#!/bin/bash
set -euo pipefail

export PATH="$TMT_TREE/.venv/bin:$PATH"
cd "$TMT_TREE"
python3 -m pytest -v tests/unittests/

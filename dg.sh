#!/bin/sh

proj_cli_dir="$(dirname "$(readlink -f "$0")")"

export PYTHONPATH="$proj_cli_dir/distgen:${PYTHONPATH+:$PYTHONPATH}"
export PATH="$proj_cli_dir/bin:${PATH+:$PATH}"

export DG_TPLDIR="$proj_cli_dir/templates"
export DG_DISTCONFDIR="$proj_cli_dir/distconf"

dg "$@"

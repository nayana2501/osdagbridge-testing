#!/usr/bin/env bash
# Screencast helper: run in a terminal while screen-recording. Pauses let viewers read.
# Usage: OSDAGBRIDGE_REPO=/path/to/OsdagBridge ./demo.sh
set -u
REPO="${OSDAGBRIDGE_REPO:-../OsdagBridge}"
say() { printf '\n\033[1;36m### %s\033[0m\n' "$1"; sleep "${2:-3}"; }

say "1. The upstream test-suite is green..."
(cd "$REPO" && python -m pytest -q 2>&1 | tail -3); sleep 3

say "2. ...yet the package core cannot be imported (ISSUE-001)"
python -I -c "import sys; sys.path.insert(0,'$REPO/src'); import osdagbridge.core.utils.units" 2>&1 | tail -1; sleep 4

say "3. The documented CLI accepts a file that does not exist (ISSUE-004)"
python -I -c "import sys; sys.path.insert(0,'$REPO/src'); sys.argv=['x','analyze','missing.yaml']; import runpy; runpy.run_module('osdagbridge.cli', run_name='__main__')"; echo "exit status: $?"; sleep 4

say "4. Our suite: 17 pass, 46 documented defects (expected failures)"
OSDAGBRIDGE_REPO="$REPO" python -m pytest -q -rx 2>&1 | tail -12; sleep 5

say "5. Same suite with --runxfail shows the raw failures"
OSDAGBRIDGE_REPO="$REPO" python -m pytest -q --runxfail 2>&1 | tail -2; sleep 4

say "6. Issue register generated from issues/issues.yaml"
head -22 issues/ISSUES.md; sleep 5

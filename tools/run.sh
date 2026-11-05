#!/usr/bin/env bash
# Run one shell command from the repository root, print its output, and append
# the command, its exact combined output and its exit status to RUN-LOG.md.
# Usage: tools/run.sh '<command>'
set -u
log="${RUN_LOG:-RUN-LOG.md}"
cmd="$1"
out="$(bash -o pipefail -c "$cmd" 2>&1)"
rc=$?
[ -n "$out" ] && printf '%s\n' "$out"
{
  printf '\n````console\n$ %s\n' "$cmd"
  [ -n "$out" ] && printf '%s\n' "$out"
  printf '[exit %d, %s]\n````\n' "$rc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "$log"
exit "$rc"

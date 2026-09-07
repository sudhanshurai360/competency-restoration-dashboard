#!/bin/bash
# push_and_sync.sh — push to GitHub (if a remote is configured yet), then sync the working tree
# to a local backup mirror.
#
# A GitHub remote was added shortly after this script's creation (2026-09-07); the push-step
# skip below is deliberately kept anyway (rather than assuming a remote always exists) so this
# script degrades gracefully if ever run in a fresh clone or fork with no remote configured yet.
#
# Requires COMPETENCY_DASHBOARD_MIRROR_DIR set in the environment (e.g. in your shell profile) to
# the mirror's local path -- deliberately not hardcoded here, so this script can be committed to a
# public-facing repo without embedding any machine- or account-specific path.
#
# Usage: ./push_and_sync.sh [git push args...]
#   No args -> `git push origin main` (only if origin exists). Any args are passed through to
#   `git push` as-is.
set -euo pipefail
cd "$(dirname "$0")"

if git remote get-url origin >/dev/null 2>&1; then
    if [ "$#" -eq 0 ]; then
        git push origin main
    else
        git push "$@"
    fi
else
    echo "No 'origin' remote configured yet -- skipping push, syncing to the mirror only." >&2
fi

if [ -z "${COMPETENCY_DASHBOARD_MIRROR_DIR:-}" ]; then
    echo "COMPETENCY_DASHBOARD_MIRROR_DIR is not set -- skipping the mirror sync." >&2
    echo "Set it in your shell profile to the mirror's local path to enable this step." >&2
    exit 0
fi

rsync -a --exclude .git --exclude .DS_Store "$(pwd)/" "$COMPETENCY_DASHBOARD_MIRROR_DIR/"
echo "Synced working tree -> \$COMPETENCY_DASHBOARD_MIRROR_DIR"

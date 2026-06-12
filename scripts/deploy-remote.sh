#!/usr/bin/env bash
#
# Sync this extension's source to a remote host (e.g. the Arduino UNO Q) for
# on-board development with F5, and optionally install/build there.
#
# Usage:
#   scripts/deploy-remote.sh [user@host] [options]
#   yarn deploy:remote -- [user@host] [options]
#
# Host resolution order:   $1 (if not a flag)  >  $APPLAB_REMOTE_HOST
# Remote dir resolution:   --dir PATH  >  $APPLAB_REMOTE_DIR  >  ~/vscode-arduino-app-cli
#
# Options:
#   --dir PATH     Destination directory on the remote (default ~/vscode-arduino-app-cli)
#   --install      Run a dependency install on the remote after syncing
#   --build        Imply --install, then run a production build on the remote
#   --no-delete    Do not delete remote files missing locally (default mirrors)
#   --dry-run      Show what rsync would transfer, change nothing
#   -h, --help     Show this help
#
# Notes:
#   --install/--build need a Node toolchain (node + yarn or npm) ON THE REMOTE.
#   If the board has no Node, skip them and just install the prebuilt .vsix
#   instead (see README "Option A").
set -euo pipefail

HOST="${APPLAB_REMOTE_HOST:-}"
REMOTE_DIR="${APPLAB_REMOTE_DIR:-\$HOME/vscode-arduino-app-cli}"
DO_INSTALL=0
DO_BUILD=0
DELETE="--delete"
DRY_RUN=""

# First non-flag argument is the host.
if [[ $# -gt 0 && "${1:0:1}" != "-" ]]; then
  HOST="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) REMOTE_DIR="$2"; shift 2 ;;
    --install) DO_INSTALL=1; shift ;;
    --build) DO_INSTALL=1; DO_BUILD=1; shift ;;
    --no-delete) DELETE=""; shift ;;
    --dry-run) DRY_RUN="--dry-run"; shift ;;
    -h|--help) sed -n '2,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//; s/^#//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$HOST" ]]; then
  echo "Error: no remote host. Pass user@host or set APPLAB_REMOTE_HOST." >&2
  echo "Try: scripts/deploy-remote.sh arduino@linucs --install" >&2
  exit 2
fi

# Repo root = parent of this script's directory.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "→ Syncing $ROOT/  →  $HOST:$REMOTE_DIR/"
# shellcheck disable=SC2086
rsync -az $DELETE $DRY_RUN \
  --exclude node_modules \
  --exclude dist \
  --exclude out \
  --exclude .vscode-test \
  --exclude '*.vsix' \
  --exclude .DS_Store \
  --exclude .git \
  -e ssh \
  "$ROOT/" "$HOST:$REMOTE_DIR/"

if [[ -n "$DRY_RUN" ]]; then
  echo "✓ Dry run complete (nothing changed)."
  exit 0
fi
echo "✓ Synced."

if [[ "$DO_INSTALL" -eq 1 ]]; then
  # Prefer yarn, fall back to npm; build if requested.
  REMOTE_CMD="cd \"$REMOTE_DIR\" && \
    if command -v yarn >/dev/null 2>&1; then PM=yarn; \
    elif command -v npm >/dev/null 2>&1; then PM=npm; \
    else echo 'No yarn/npm on remote — install nodejs/npm or use the .vsix route.' >&2; exit 1; fi; \
    echo \"Using \$PM\"; \$PM install"
  if [[ "$DO_BUILD" -eq 1 ]]; then
    REMOTE_CMD="$REMOTE_CMD && \$PM run compile"
  fi
  echo "→ Installing on $HOST…"
  # shellcheck disable=SC2029
  ssh "$HOST" "bash -lc '$REMOTE_CMD'"
  echo "✓ Remote install complete."
fi

echo "Done. Open the folder on $HOST via Remote-SSH and press F5 to launch."

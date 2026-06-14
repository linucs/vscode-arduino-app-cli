#!/usr/bin/env bash
#
# Download the Arduino App daemon's OpenAPI spec to api/openapi.yaml.
#
# The daemon serves Swagger UI at /v1/docs/ and the raw spec at
# /v1/docs/openapi.yaml. Keeping a checked-in copy lets us diff the
# AppLabClient REST surface against the source of truth (see the bug where
# `createApp` sent `no_sketch` in the body instead of the `skip-sketch` query).
#
# Usage:
#   scripts/fetch-openapi.sh                 # 127.0.0.1:8800
#   APPLAB_HOST=board.local APPLAB_PORT=8800 scripts/fetch-openapi.sh
set -euo pipefail

HOST="${APPLAB_HOST:-127.0.0.1}"
PORT="${APPLAB_PORT:-8800}"
BASE="http://${HOST}:${PORT}"
OUT_DIR="$(cd "$(dirname "$0")/.." && pwd)/api"
OUT="${OUT_DIR}/openapi.yaml"

mkdir -p "${OUT_DIR}"

echo "Fetching OpenAPI spec from ${BASE}/v1/docs/openapi.yaml …"
if ! curl -fsS --max-time 15 "${BASE}/v1/docs/openapi.yaml" -o "${OUT}"; then
  echo "error: could not reach the daemon at ${BASE}." >&2
  echo "       Is arduino-app-cli's daemon running? (systemd on the UNO Q, or locally)" >&2
  exit 1
fi

LINES="$(wc -l < "${OUT}" | tr -d ' ')"
echo "Wrote ${OUT} (${LINES} lines)."

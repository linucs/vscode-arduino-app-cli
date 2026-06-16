#!/usr/bin/env bash
#
# Generate the Arduino Python type stubs (.pyi) shipped with the extension.
#
# App Lab apps import `arduino.app_utils` / `arduino.app_bricks.*` from the
# `arduino_app_bricks` package, which is baked into the `python-apps-base` Docker
# image (not on the host, not on PyPI). Pylance therefore can't resolve those
# imports. This script produces a stub tree under `stubs/arduino/**` that the
# extension copies into a workspace's `typings/` at "Configure IntelliSense" time.
#
# It is a MAINTAINER step, run when bumping the pinned framework version — NOT part
# of release CI. The output is committed and shipped in the .vsix.
#
# stubgen runs in its default parse (AST) mode: it does NOT import the framework,
# so the package's optional brick dependencies (langchain, paho, …) need not be
# installed and its custom build backend is never invoked.
#
# Usage:
#   yarn gen:stubs
#   FRAMEWORK_REF=release/0.11.0 yarn gen:stubs
#   FRAMEWORK_SRC=../app-bricks-py yarn gen:stubs   # offline: use a local checkout
set -euo pipefail

# --- config -----------------------------------------------------------------
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/stubs"
OVERRIDES="$ROOT/stubs-overrides"

# Pinned framework tag — single source of truth, committed at .framework-ref and
# read by both `yarn gen:stubs` and the release workflow. Env override wins.
DEFAULT_REF="$(tr -d '[:space:]' < "$ROOT/.framework-ref" 2>/dev/null || true)"
FRAMEWORK_REF="${FRAMEWORK_REF:-${DEFAULT_REF:-release/0.10.0rc1}}"
# Public repo — anonymous HTTPS clone works with no auth, so anyone who clones this
# repo can run `yarn gen:stubs`. Override with the SSH URL if you prefer.
FRAMEWORK_URL="${FRAMEWORK_URL:-https://github.com/arduino/app-bricks-py.git}"
FRAMEWORK_SRC="${FRAMEWORK_SRC:-}" # optional local checkout (skips the clone)

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

# --- 1. obtain the framework source at the pinned ref -----------------------
if [ -n "$FRAMEWORK_SRC" ]; then
  SRC_ROOT="$(cd "$FRAMEWORK_SRC" && pwd)"
  REF_DESC="local:$SRC_ROOT"
  echo "Using local framework source: $SRC_ROOT"
else
  echo "Cloning $FRAMEWORK_URL @ $FRAMEWORK_REF …"
  git clone --depth 1 --branch "$FRAMEWORK_REF" "$FRAMEWORK_URL" "$TMP/framework"
  SRC_ROOT="$TMP/framework"
  REF_DESC="$FRAMEWORK_REF $(git -C "$SRC_ROOT" rev-parse --short HEAD)"
fi
SEARCH="$SRC_ROOT/src"
if [ ! -d "$SEARCH/arduino" ]; then
  echo "error: $SEARCH/arduino not found — unexpected framework layout" >&2
  exit 1
fi

# --- 2. throwaway venv with mypy (stubgen) ----------------------------------
echo "Setting up stubgen (mypy) in a throwaway venv …"
python3 -m venv "$TMP/venv"
# shellcheck disable=SC1091
"$TMP/venv/bin/pip" install --quiet --upgrade pip
"$TMP/venv/bin/pip" install --quiet mypy
STUBGEN="$TMP/venv/bin/stubgen"

# --include-docstrings (hover text) was added in newer mypy; use it when available.
DOC_FLAG=""
if "$STUBGEN" --help 2>&1 | grep -q -- "--include-docstrings"; then
  DOC_FLAG="--include-docstrings"
fi

# --- 3. stage the source we want stubbed ------------------------------------
# `arduino` is a PEP420 namespace package (no __init__.py). stubgen roots modules
# at the first ancestor lacking __init__.py, so without help it flattens
# app_bricks/* up to the top level. We stage a copy, drop build-tooling + example
# subpackages (not app API), and add `arduino/__init__.py` so stubgen roots at the
# staging dir and preserves the full `arduino.app_bricks.<brick>` dotted paths.
WORK="$TMP/stage"
mkdir -p "$WORK"
cp -R "$SEARCH/arduino" "$WORK/arduino"
rm -rf "$WORK/arduino/app_tools" "$WORK/arduino/app_blocks"
find "$WORK/arduino" -type d -name examples -prune -exec rm -rf {} +
touch "$WORK/arduino/__init__.py"

# --- 4. generate stubs (parse mode — no framework imports) ------------------
echo "Running stubgen …"
"$STUBGEN" "$WORK/arduino" -o "$TMP/out" $DOC_FLAG >/dev/null

if [ ! -d "$TMP/out/arduino" ]; then
  echo "error: stubgen produced no arduino/ package" >&2
  exit 1
fi

# Give the namespace subpackages (app_bricks, app_internal, app_peripherals) an
# empty __init__.pyi so the stub tree resolves as regular packages under typings/.
find "$TMP/out/arduino" -type d -exec sh -c '[ -e "$1/__init__.pyi" ] || : > "$1/__init__.pyi"' _ {} \;

# --- 4. replace the committed stub tree -------------------------------------
rm -rf "$OUT/arduino"
mkdir -p "$OUT"
cp -R "$TMP/out/arduino" "$OUT/arduino"

# --- 5a. targeted typing fixes ----------------------------------------------
# stubgen widens module-level singletons (`X = SomeClass()`) to `X: Incomplete`,
# which kills completions for the two most-used public symbols. Re-point them at
# their concrete classes (both defined in the same stub file).
perl -0pi -e 's/^App: Incomplete$/App: AppController/m' "$OUT/arduino/app_utils/app.pyi"
perl -0pi -e 's/^brick: Incomplete$/brick: BrickDecorator/m' "$OUT/arduino/app_utils/brick.pyi"

# --- 5b. overlay hand-authored fixes (optional) -----------------------------
# Drop full-file .pyi replacements under stubs-overrides/arduino/** for anything
# stubgen can't express. None needed today (ArduinoCloud already emits __getattr__).
if [ -d "$OVERRIDES" ]; then
  echo "Applying overrides from stubs-overrides/ …"
  cp -R "$OVERRIDES/." "$OUT/arduino/"
fi

# --- 6. markers -------------------------------------------------------------
touch "$OUT/arduino/py.typed"
printf '%s\n' "$REF_DESC" > "$OUT/STUBS_VERSION"

COUNT="$(find "$OUT/arduino" -name '*.pyi' | wc -l | tr -d ' ')"
echo "Done: $COUNT .pyi files under stubs/arduino (framework $REF_DESC)"

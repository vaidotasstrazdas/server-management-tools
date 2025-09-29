#!/usr/bin/env bash
set -euo pipefail

# -------- Settings --------
ROOT="$(cd "$(dirname "$0")" && pwd)"
TOOLS_DIR="$ROOT/tools"
SRC_DIR="$ROOT/src"
BUILD_DIR="$ROOT/build"
DIST_DIR="$ROOT/dist"
DATA_DIR="$ROOT/data"
PYTHON="${PYTHON:-python3}"

echo "Using Python: $("$PYTHON" -V)"

rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

"$PYTHON" -m pip install --upgrade pip >/dev/null

build_tool() {
  local tool_name="$1"
  local tool_src_dir="$TOOLS_DIR/$tool_name"

  if [[ ! -d "$tool_src_dir" ]]; then
    echo "Skipping '$tool_name' (not a directory)"
    return
  fi

  if [[ ! -f "$tool_src_dir/main.py" ]]; then
    echo "Skipping '$tool_name' (no main.py found)"
    return
  fi

  local stage_dir="$BUILD_DIR/$tool_name"
  mkdir -p "$stage_dir"

  echo "==== Building tool: $tool_name ===="

  if [[ -d "$SRC_DIR" ]]; then
    cp -R "$SRC_DIR/"* "$stage_dir/" 2>/dev/null || true
  fi

  mkdir -p "$stage_dir/$tool_name"
  cp -R "$tool_src_dir/"* "$stage_dir/$tool_name/"

  if [[ -f "$tool_src_dir/requirements.txt" && -s "$tool_src_dir/requirements.txt" ]]; then
    "$PYTHON" -m pip install --no-warn-script-location --target "$stage_dir" -r "$tool_src_dir/requirements.txt"
  fi

  local out_pyz="$DIST_DIR/$tool_name.pyz"
  "$PYTHON" -m zipapp "$stage_dir" \
    -m "$tool_name.main:main" \
    -o "$out_pyz" \
    -p "/usr/bin/env python3"

  chmod +x "$out_pyz"

  echo "Built: $out_pyz"
  echo "Run:   $out_pyz"
  echo
}

if [[ $# -gt 0 ]]; then
  for t in "$@"; do
    build_tool "$t"
  done
else
  if [[ -d "$TOOLS_DIR" ]]; then
    shopt -s nullglob
    for dir in "$TOOLS_DIR"/*/; do
      tool_name="$(basename "$dir")"
      build_tool "$tool_name"
    done
    shopt -u nullglob
  else
    echo "No tools directory found at $TOOLS_DIR"
    exit 1
  fi
fi

echo "Copying data dir to the dist"
mkdir -p "$DIST_DIR/data"
cp -R "$DATA_DIR/"* "$DIST_DIR/data" 2>/dev/null || true

echo "All done. Artifacts are in: $DIST_DIR"

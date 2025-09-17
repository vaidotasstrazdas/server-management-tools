#!/usr/bin/env bash
set -euo pipefail

# -------- Settings --------
ROOT="$(cd "$(dirname "$0")" && pwd)"
TOOLS_DIR="$ROOT/tools"
SRC_DIR="$ROOT/src"
BUILD_DIR="$ROOT/build"
DIST_DIR="$ROOT/dist"
PYTHON="${PYTHON:-python3}"   # allow override: PYTHON=/path/to/python3 ./build_tools.sh

echo "Using Python: $("$PYTHON" -V)"

# -------- Clean output dirs --------
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# -------- Upgrade pip once (faster overall) --------
"$PYTHON" -m pip install --upgrade pip >/dev/null

# -------- Helper: build one tool --------
build_tool() {
  local tool_name="$1"
  local tool_src_dir="$TOOLS_DIR/$tool_name"

  # Validate expected layout
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

  # 1) Stage shared packages from src/*
  if [[ -d "$SRC_DIR" ]]; then
    # Copy all top-level packages/modules from src into the stage root
    # so imports like 'from packages_engine ...' work.
    cp -R "$SRC_DIR/"* "$stage_dir/" 2>/dev/null || true
  fi

  # 2) Stage the tool's own code under a namespaced folder: <tool_name>/
  #    This lets the entry point be '<tool>.main:main' and supports any local imports.
  mkdir -p "$stage_dir/$tool_name"
  cp -R "$tool_src_dir/"* "$stage_dir/$tool_name/"

  # 3) Vendor dependencies into the SAME stage dir
  #    - Per-tool requirements.txt if present
  if [[ -f "$tool_src_dir/requirements.txt" && -s "$tool_src_dir/requirements.txt" ]]; then
    "$PYTHON" -m pip install --no-warn-script-location --target "$stage_dir" -r "$tool_src_dir/requirements.txt"
  fi

  # 4) Build the zipapp with entry point '<tool>.main:main'
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

# -------- Discover tools and build --------
# Build all immediate subdirectories in tools/ (optionally filtered by args)
if [[ $# -gt 0 ]]; then
  # Build only tools passed as arguments
  for t in "$@"; do
    build_tool "$t"
  done
else
  # Build all subdirectories of tools/
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

echo "All done. Artifacts are in: $DIST_DIR"

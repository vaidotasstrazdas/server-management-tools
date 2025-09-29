#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$ROOT/dist"
SUGGESTED_PATH=$(diskutil list | grep "external" | cut -d " " -f 1)
echo -n "Deployment path (suggested path: '$SUGGESTED_PATH/bin'): "
read DEPLOYMENT_PATH
DEPLOYMENT_PATH="$DEPLOYMENT_PATH/bin"

if [ -z "${DEPLOYMENT_PATH}" ]; then
  echo "Not entered."
  exit 1
fi

echo "Deploying to $DEPLOYMENT_PATH"
rm -rf "$DEPLOYMENT_PATH" || true
mkdir -p "$DEPLOYMENT_PATH"
cp -R "$DIST_DIR/"* "$DEPLOYMENT_PATH" 2>/dev/null || true
echo "Deployment done."
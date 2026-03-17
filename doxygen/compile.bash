#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export LIMEF_VERSION="$(cat "$SCRIPT_DIR/../../VERSION")"
doxygen Doxyfile 2>&1 | grep -i "warn\|error"

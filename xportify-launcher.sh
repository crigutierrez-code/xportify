#!/usr/bin/env bash
DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
cd "$DIR"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
exec "$DIR/.venv/bin/python" "$DIR/main.py" "$@"

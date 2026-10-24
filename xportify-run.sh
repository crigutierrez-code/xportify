#!/usr/bin/env bash
DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
cd "$DIR"
exec "$DIR/.venv/bin/python" "$DIR/main.py"

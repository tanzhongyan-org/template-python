#!/bin/sh
set -e

MODE="${1:-post-edit}"
INPUT="$(cat || true)"

if [ "$MODE" = "post-edit" ]; then
  FILE_PATH="$2"
  if [ -z "$FILE_PATH" ] && [ -n "$INPUT" ]; then
    FILE_PATH="$(echo "$INPUT" | grep -o '"file_path"[^,]*' | cut -d'"' -f4 || true)"
  fi
  if [ -n "$FILE_PATH" ] && [ -f "$FILE_PATH" ]; then
    uv run ruff check --fix "$FILE_PATH" >/dev/null 2>&1 || true
    uv run ruff format "$FILE_PATH" >/dev/null 2>&1 || true
  fi
  exit 0
fi

if [ "$MODE" = "stop" ]; then
  MARKER=".git/agent-hook-stop-blocked"
  if echo "$INPUT" | grep -q '"stop_hook_active":\s*true' || [ -f "$MARKER" ]; then
    rm -f "$MARKER"
    exit 0
  fi

  if make check; then
    rm -f "$MARKER"
    exit 0
  else
    touch "$MARKER"
    echo "Verification check failed. Fix errors before finishing turn." >&2
    echo '{"decision": "block", "reason": "Verification check failed. Fix errors before finishing turn."}'
    exit 2
  fi
fi

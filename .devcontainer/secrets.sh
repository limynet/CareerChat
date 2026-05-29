#!/usr/bin/env bash
# Map Gitpod user secrets to standard env vars for CareerChat
# Gitpod secrets are injected into the container env; this script aliases them.

set -euo pipefail

SECRETS_FILE="/workspaces/CareerChat/.env.local"

map_secret() {
  local from="$1"
  local to="$2"
  if [ -n "$(printenv "$from" 2>/dev/null || true)" ]; then
    echo "export $to=\"\$$from\"" >> "$SECRETS_FILE"
  fi
}

> "$SECRETS_FILE"

# Map user's secret names to standard variable names
map_secret "z_ai"        "OPENAI_API_KEY"
map_secret "z_api"       "OPENAI_API_KEY"
map_secret "gemini_api"  "GEMINI_API_KEY"
map_secret "poe_api"     "POE_API_KEY"

# Foundry / Vantage vars (if set)
map_secret "FOUNDRY_URL"    "FOUNDRY_URL"
map_secret "FOUNDRY_TOKEN"  "FOUNDRY_TOKEN"

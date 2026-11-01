#!/bin/bash
# The forced command for the GitHub Actions deploy key (see "Automatic deploys" in README.md).
# Installed at ~/apps/tds-hub/deploy-launcher.sh, beside the checkout rather than inside it,
# so the git reset below can never rewrite this script while it runs.
set -euo pipefail

CHECKOUT_DIR="$HOME/apps/tds-hub/repo"

cd "$CHECKOUT_DIR"
git fetch --depth 1 origin main
git reset --hard origin/main

cd deploy
# Recreates the container only if compose.yaml changed; otherwise a no-op.
docker compose up -d --wait
# The site is bind-mounted so it's live already; reload nginx in case nginx.conf changed.
docker compose exec -T web nginx -s reload
# 127.0.0.1, not localhost: on an IPv6-capable host, localhost resolves to ::1 inside the
# container first, and nginx only listens on IPv4.
docker compose exec -T web wget -qO- http://127.0.0.1:8000/healthz
echo "tds-hub deployed: $(git -C "$CHECKOUT_DIR" rev-parse --short HEAD)"

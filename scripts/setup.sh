#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo
echo "================================================"
echo "          CYBERVOYRAX Workspace Setup"
echo "================================================"
echo
echo "WARNING:"
echo "CYBERVOYRAX is intentionally vulnerable."
echo "Run it only in an authorized/local lab environment."
echo "Do not expose it directly to the public internet."
echo

bash scripts/check_requirements.sh

echo
echo "[*] Building and starting CYBERVOYRAX..."
echo

docker compose up -d --build

echo
echo "[*] Waiting for the application container..."

for i in {1..60}; do
    if docker compose exec -T web true >/dev/null 2>&1; then
        break
    fi

    if [[ "$i" -eq 60 ]]; then
        echo
        echo "[✗] Web container did not become ready."
        echo
        docker compose logs --tail=100 web
        exit 1
    fi

    sleep 2
done

echo "[✓] Containers started"

echo
echo "[*] Provisioning assessment account..."
bash scripts/provision_lab_accounts.sh

echo
echo "[*] Verifying account baseline..."
docker compose exec -T web python scripts/verify_account_baseline.py

APP_PORT_VALUE="${APP_PORT:-5000}"

if [[ -f ".env" ]]; then
    ENV_PORT="$(sed -n 's/^APP_PORT=//p' .env | tail -n1)"
    if [[ -n "$ENV_PORT" ]]; then
        APP_PORT_VALUE="$ENV_PORT"
    fi
fi

echo
echo "================================================"
echo "          CYBERVOYRAX is ready"
echo "================================================"
echo
echo "URL:"
echo "  http://127.0.0.1:${APP_PORT_VALUE}"
echo
echo "Assessment credentials:"
echo "  .lab-credentials"
echo
echo "View them with:"
echo "  cat .lab-credentials"
echo

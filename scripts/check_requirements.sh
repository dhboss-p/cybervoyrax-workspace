#!/usr/bin/env bash
set -euo pipefail

echo
echo "=============================================="
echo "       CYBERVOYRAX Environment Check"
echo "=============================================="
echo

FAILED=0

check_command() {
    local cmd="$1"
    local name="$2"

    if command -v "$cmd" >/dev/null 2>&1; then
        echo "[✓] $name detected"
    else
        echo "[✗] $name not found"
        FAILED=1
    fi
}

check_command git "Git"
check_command docker "Docker"

if command -v docker >/dev/null 2>&1; then
    if docker compose version >/dev/null 2>&1; then
        echo "[✓] Docker Compose v2 detected"
    else
        echo "[✗] Docker Compose v2 not available"
        FAILED=1
    fi

    if docker info >/dev/null 2>&1; then
        echo "[✓] Docker daemon running"
    else
        echo "[✗] Docker daemon is not running or access is denied"
        FAILED=1
    fi
fi

echo

if [[ "$FAILED" -ne 0 ]]; then
    echo "Environment is not ready."
    echo
    echo "CYBERVOYRAX requires:"
    echo "  - Git"
    echo "  - Docker"
    echo "  - Docker Compose v2"
    echo "  - A running Docker daemon"
    echo
    echo "Install/fix the missing requirement and run:"
    echo
    echo "  bash scripts/check_requirements.sh"
    echo
    exit 1
fi

echo "[✓] Environment ready for CYBERVOYRAX."

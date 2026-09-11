#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR=".upgrade-backups/update-$TIMESTAMP"

echo
echo "================================================"
echo "          CYBERVOYRAX Workspace Update"
echo "================================================"
echo
echo "This update preserves:"
echo "  - MySQL database"
echo "  - User accounts"
echo "  - Assessment credentials"
echo "  - Projects and comments"
echo "  - Uploaded documents"
echo "  - Local .env configuration"
echo

bash scripts/check_requirements.sh

# --------------------------------------------------
# Basic repository check
# --------------------------------------------------

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "[✗] This installation is not inside a Git repository."
    echo "Automatic Git updates cannot continue."
    exit 1
fi

CURRENT_COMMIT="$(git rev-parse HEAD)"

echo
echo "[*] Current version:"
echo "    $CURRENT_COMMIT"

# Refuse to overwrite local source modifications.
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    echo
    echo "[✗] Tracked source files contain local modifications."
    echo
    echo "The updater will not overwrite them automatically."
    echo
    echo "Review them with:"
    echo "  git status"
    echo "  git diff"
    echo
    exit 1
fi

# --------------------------------------------------
# Backup
# --------------------------------------------------

echo
echo "[*] Creating upgrade backup..."

mkdir -p "$BACKUP_DIR"

echo "[*] Backing up database..."

if ! docker compose ps --status running db 2>/dev/null | grep -q .; then
    echo "[✗] Database container is not running."
    echo "Start CYBERVOYRAX before updating."
    exit 1
fi

docker compose exec -T db sh -c \
'exec mysqldump \
    -uroot \
    -p"$MYSQL_ROOT_PASSWORD" \
    --single-transaction \
    --routines \
    --triggers \
    "$MYSQL_DATABASE"' \
    > "$BACKUP_DIR/database.sql"

echo "[✓] Database backup created"

if [[ -d "instance/uploads" ]]; then
    echo "[*] Backing up uploaded files..."
    tar -czf "$BACKUP_DIR/uploads.tar.gz" instance/uploads
    echo "[✓] Upload backup created"
fi

if [[ -f ".lab-credentials" ]]; then
    cp -p .lab-credentials "$BACKUP_DIR/lab-credentials"
    echo "[✓] Assessment credentials backed up"
fi

if [[ -f ".env" ]]; then
    cp -p .env "$BACKUP_DIR/env"
    echo "[✓] Local environment backed up"
fi

printf '%s\n' "$CURRENT_COMMIT" > "$BACKUP_DIR/source-version.txt"

echo
echo "[✓] Backup stored in:"
echo "    $BACKUP_DIR"

# --------------------------------------------------
# Download source update
# --------------------------------------------------

echo
echo "[*] Checking for updates..."

git fetch origin

CURRENT_BRANCH="$(git branch --show-current)"

if [[ -z "$CURRENT_BRANCH" ]]; then
    echo "[✗] Detached Git HEAD detected."
    echo "Switch to the normal CYBERVOYRAX branch before updating."
    exit 1
fi

LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse "origin/$CURRENT_BRANCH")"

if [[ "$LOCAL" == "$REMOTE" ]]; then
    echo "[✓] Source is already up to date."
else
    echo "[*] Installing source update..."
    git pull --ff-only origin "$CURRENT_BRANCH"
    echo "[✓] Source updated"
fi

# --------------------------------------------------
# Rebuild application
# --------------------------------------------------

echo
echo "[*] Rebuilding CYBERVOYRAX..."

if ! docker compose up -d --build; then
    echo
    echo "[✗] Container rebuild failed."
    echo
    echo "Your backup is safe at:"
    echo "    $BACKUP_DIR"
    exit 1
fi

# --------------------------------------------------
# Wait for web container
# --------------------------------------------------

echo
echo "[*] Waiting for application startup..."

READY=0

for i in {1..60}; do
    if docker compose exec -T web true >/dev/null 2>&1; then
        READY=1
        break
    fi

    sleep 2
done

if [[ "$READY" -ne 1 ]]; then
    echo
    echo "[✗] Web container did not become available."
    echo
    docker compose logs --tail=100 web
    echo
    echo "Backup:"
    echo "    $BACKUP_DIR"
    exit 1
fi

# Give startup migrations/bootstrap a moment to finish.
sleep 3

# --------------------------------------------------
# Verification
# --------------------------------------------------

echo
echo "[*] Verifying database/account baseline..."

if ! docker compose exec -T web \
    python scripts/verify_account_baseline.py; then

    echo
    echo "[✗] Post-update verification failed."
    echo
    echo "Do NOT delete your backup:"
    echo "    $BACKUP_DIR"
    echo
    echo "Inspect:"
    echo "    docker compose logs --tail=150 web"
    exit 1
fi

NEW_COMMIT="$(git rev-parse HEAD)"

APP_PORT_VALUE="${APP_PORT:-5000}"

if [[ -f ".env" ]]; then
    ENV_PORT="$(sed -n 's/^APP_PORT=//p' .env | tail -n1)"
    if [[ -n "$ENV_PORT" ]]; then
        APP_PORT_VALUE="$ENV_PORT"
    fi
fi

echo
echo "================================================"
echo "          CYBERVOYRAX Update Complete"
echo "================================================"
echo
echo "Previous source:"
echo "  $CURRENT_COMMIT"
echo
echo "Current source:"
echo "  $NEW_COMMIT"
echo
echo "Application:"
echo "  http://127.0.0.1:${APP_PORT_VALUE}"
echo
echo "Backup:"
echo "  $BACKUP_DIR"
echo
echo "Existing assessment credentials were preserved."
echo

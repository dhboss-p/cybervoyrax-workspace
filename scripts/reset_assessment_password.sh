#!/usr/bin/env bash
set -euo pipefail

CREDENTIAL_FILE="${1:-.lab-credentials}"
ASSESSMENT_EMAIL="assessor@cybervoyrax.test"

echo
echo "CYBERVOYRAX Assessment Account Recovery"
echo "----------------------------------------"
echo
echo "This will reset the assessment account password."
echo

read -r -p "Continue? [y/N] " CONFIRM

case "$CONFIRM" in
    y|Y|yes|YES)
        ;;
    *)
        echo "Reset cancelled."
        exit 0
        ;;
esac

echo
echo "[*] Resetting assessment password..."

OUTPUT="$(
    docker compose exec -T web \
        python scripts/reset_assessment_password.py
)"

NEW_PASSWORD="$(
    printf '%s\n' "$OUTPUT" |
    sed -n 's/^ASSESSMENT_PASSWORD=//p' |
    tail -n1
)"

if [[ -z "$NEW_PASSWORD" ]]; then
    echo "[✗] Password reset did not return a new password."
    exit 1
fi

umask 077

cat > "$CREDENTIAL_FILE" <<EOF2
ASSESSMENT_EMAIL=$ASSESSMENT_EMAIL
ASSESSMENT_PASSWORD=$NEW_PASSWORD
EOF2

chmod 600 "$CREDENTIAL_FILE"

echo
echo "[✓] Assessment password reset."
echo "[✓] Existing assessment sessions invalidated."
echo "[✓] Credentials updated: $CREDENTIAL_FILE"
echo
echo "View the new credentials with:"
echo "  cat $CREDENTIAL_FILE"
echo

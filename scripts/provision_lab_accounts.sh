#!/usr/bin/env bash
set -euo pipefail

CREDENTIAL_FILE="${1:-.lab-credentials}"
ASSESSMENT_EMAIL="assessor@cybervoyrax.test"

if [[ -f "$CREDENTIAL_FILE" ]]; then
  ASSESSMENT_PASSWORD="$(sed -n 's/^ASSESSMENT_PASSWORD=//p' "$CREDENTIAL_FILE" | head -n1)"
fi

if [[ -z "${ASSESSMENT_PASSWORD:-}" ]]; then
  ASSESSMENT_PASSWORD="$(python - <<'PY2'
import secrets
print('CVX-' + secrets.token_urlsafe(24))
PY2
)"
  umask 077
  cat > "$CREDENTIAL_FILE" <<EOF
ASSESSMENT_EMAIL=$ASSESSMENT_EMAIL
ASSESSMENT_PASSWORD=$ASSESSMENT_PASSWORD
EOF
  chmod 600 "$CREDENTIAL_FILE"
fi

docker compose exec -T -e ASSESSMENT_PASSWORD="$ASSESSMENT_PASSWORD" web python scripts/provision_phase63_accounts.py

echo
echo "Assessment credentials are stored locally in: $CREDENTIAL_FILE"
echo "Run: cat $CREDENTIAL_FILE"

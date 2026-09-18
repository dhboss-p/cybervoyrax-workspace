#!/usr/bin/env bash
set -euo pipefail

CREDENTIAL_FILE="${1:-.lab-credentials}"
ASSESSMENT_EMAIL="assessor@cybervoyrax.test"

# Check whether the assessment account already exists.
ASSESSOR_EXISTS="$(
docker compose exec -T web python - <<'PY'
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    row = db.fetch_one(
        "SELECT id FROM users WHERE LOWER(email)=LOWER(%s) LIMIT 1",
        ("assessor@cybervoyrax.test",),
    )
    print("yes" if row else "no")
PY
)"

if [[ "$ASSESSOR_EXISTS" == "yes" ]]; then
    echo "Assessment account already exists."
    echo "Existing password preserved."

    if [[ -f "$CREDENTIAL_FILE" ]]; then
        echo "Existing credential file preserved: $CREDENTIAL_FILE"
    else
        echo
        echo "NOTE:"
        echo "The assessment account exists, but $CREDENTIAL_FILE is missing."
        echo "A replacement password was NOT generated."
        echo "Use the explicit password-reset workflow if access has been lost."
    fi

    exit 0
fi

# Account does not exist, so this is its initial provisioning.
ASSESSMENT_PASSWORD="$(
python3 - <<'PY'
import secrets
print("CVX-" + secrets.token_urlsafe(24))
PY
)"

echo "Creating assessment account..."

docker compose exec -T \
    -e ASSESSMENT_PASSWORD="$ASSESSMENT_PASSWORD" \
    web \
    python scripts/provision_phase63_accounts.py

# Only write credentials after successful account creation.
umask 077

cat > "$CREDENTIAL_FILE" <<EOF2
ASSESSMENT_EMAIL=$ASSESSMENT_EMAIL
ASSESSMENT_PASSWORD=$ASSESSMENT_PASSWORD
EOF2

chmod 600 "$CREDENTIAL_FILE"

echo
echo "Assessment account created."
echo "Initial credentials stored locally in: $CREDENTIAL_FILE"
echo "Run: cat $CREDENTIAL_FILE"

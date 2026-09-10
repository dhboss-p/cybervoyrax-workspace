#!/usr/bin/env bash
set -euo pipefail

echo "CYBERVOYRAX Workspace — Phase 6.1 upgrade"
mkdir -p .upgrade-backups
backup=".upgrade-backups/pre-phase61-$(date +%Y%m%d-%H%M%S).tar.gz"
tar --exclude='./.upgrade-backups' --exclude='./.git' -czf "$backup" .
echo "Backup created: $backup"

docker-compose down
docker-compose build web
docker-compose up -d

echo "Waiting for the application..."
for i in $(seq 1 40); do
  if docker-compose exec -T web python -c "from app import create_app; a=create_app(); assert a.config['APP_VERSION']=='0.6.1-phase6.1'; print(a.config['APP_VERSION'])" >/dev/null 2>&1; then
    docker-compose exec -T web python scripts/verify_phase61.py
    docker-compose ps
    echo "Phase 6.1 is running."
    exit 0
  fi
  sleep 2
done

docker-compose logs --tail=120 web
exit 1

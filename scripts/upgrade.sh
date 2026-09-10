#!/usr/bin/env bash
set -euo pipefail

docker-compose down
docker-compose build web
docker-compose up -d

echo "Waiting for CYBERVOYRAX Workspace..."
for i in $(seq 1 30); do
  if docker-compose exec -T web python -c "from app import create_app; print(create_app().config['APP_VERSION'])" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

docker-compose ps

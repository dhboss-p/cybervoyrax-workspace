#!/usr/bin/env bash
set -euo pipefail

docker-compose down
docker-compose build web
docker-compose up -d

for i in $(seq 1 40); do
  if docker-compose exec -T web python -c "from app import create_app; print(create_app().config.get('APP_VERSION'))" >/dev/null 2>&1; then
    docker-compose ps
    exit 0
  fi
  sleep 2
done

echo "Services did not become ready in time."
docker-compose logs --tail=100 web
exit 1

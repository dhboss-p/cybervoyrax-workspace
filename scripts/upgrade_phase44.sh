#!/usr/bin/env bash
set -euo pipefail

docker-compose down
docker-compose build web
docker-compose up -d

for i in $(seq 1 35); do
  if docker-compose exec -T web python -c "from app import create_app; a=create_app(); print(a.config.get('APP_VERSION'))" >/dev/null 2>&1; then
    docker-compose ps
    exit 0
  fi
  sleep 2
done

echo "Web container did not become ready in time."
docker-compose logs --tail=80 web
exit 1

#!/bin/bash

cd "$(dirname "$0")/.." || exit 1

docker compose create configurator
docker compose --env-file Deploy/.env --env-file Deploy/.env.local start configurator
bash scripts/rebuild.sh
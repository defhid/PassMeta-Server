#!/bin/bash

cd "$(dirname "$0")/.." || exit 1

docker compose create configurator
docker compose --env-file .env --env-file .env.local start configurator
bash scripts/rebuild.sh
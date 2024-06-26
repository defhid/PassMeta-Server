#!/bin/bash

cd "$(dirname "$0")/.." || exit 1

docker compose --env-file .env --env-file .env.local create configurator --force-recreate --build
docker compose run configurator
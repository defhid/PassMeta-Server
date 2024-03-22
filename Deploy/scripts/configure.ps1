$dir = Split-Path $MyInvocation.MyCommand.Path
Set-Location "$dir/.."

docker compose --env-file .env --env-file .env.local create configurator
docker compose --env-file .env --env-file .env.local start configurator
scripts/rebuild.ps1
#!/usr/bin/env bash
set -e
[ -f .env ] || cp .env.example .env
docker compose up --build -d
echo "Frontend: http://localhost:3000"
echo "Swagger:  http://localhost:8000/docs"

if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose up --build -d
Write-Host "Frontend: http://localhost:3000"
Write-Host "Swagger:  http://localhost:8000/docs"

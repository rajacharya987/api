CodeAcademy Execution Stack (MVP)
Overview:
 - api/ : FastAPI service intended to run on Fly.io. It proxies execution requests to the runner.
 - runner/: Docker-based executor service that runs arbitrary code inside ephemeral containers on a host with Docker.

Deployment options:
 - Run runner on your VPS (requires Docker). Run API on Fly.io and set RUNNER_URL to your runner's public URL.
 - For local testing, use docker-compose (not included) to link api and runner.

Security:
 - Do not expose the runner publicly without auth and firewalling.
 - Consider adding mutual TLS, API keys, and rate limits.

Notes:
 - This is an MVP to get you started. For production, consider using Firecracker microVMs, separate compile pipelines, and strict quota management.

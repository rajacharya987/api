Runner service (Docker-based)
--------------------------------
This service uses the host's Docker daemon to run each code execution inside an ephemeral container.
Requirements:
 - A Linux host with Docker installed and the `docker` CLI available.
 - Run this runner on a dedicated host or VM (not the Fly.io app), and secure access (TLS, API keys).
Deploy:
 - docker build -t code-runner .
 - docker run -p 8001:8001 --name runner --restart=unless-stopped code-runner
Security notes:
 - This runner uses --network none and resource limits, but exposing Docker dangerously can still be abused.
 - Use firewall rules and authentication in front of the runner.

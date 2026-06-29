# Distributed Rate Limiter & API Gateway

A production-style **FastAPI + Redis** gateway that implements both **Token Bucket** and **Sliding Window** rate limiting using Redis-backed shared state and atomic Lua scripts. It includes a polished dashboard, Prometheus metrics, Grafana provisioning, Docker Compose, Kubernetes manifests, tests, and a local benchmark script.

## Why this is interview-ready

This project now visibly supports the core resume story:

- Token bucket and sliding window algorithms
- Redis atomic operations with Lua scripts for correctness under concurrency
- FastAPI middleware that acts like an API gateway before protected routes execute
- Rate-limit response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`
- Prometheus metrics and Grafana dashboard provisioning
- Docker Compose for local demo
- Kubernetes deployment, service, readiness/liveness probes, and HPA
- Frontend-friendly dashboard at `/dashboard`

> Important: the repo can show the architecture and code quality, but do not claim exact `50K+ RPS`, `sub-5ms p99`, or `99.95% uptime` unless you have benchmark and uptime evidence from your own environment. Use `scripts/load_test.py` to generate numbers you can honestly discuss.

## Architecture

```text
Client / Frontend
      |
      v
FastAPI API Gateway Middleware
      |
      +-- Hash API key or client IP
      +-- Redis Lua atomic limiter check
      +-- Allow request or return HTTP 429
      |
      v
Protected API route
      |
      v
Prometheus / Grafana metrics
```

## Run locally in VS Code

### Option A: Docker Compose, easiest

```bash
git clone https://github.com/Muskaan2211/distributed-rate-limiter.git
cd distributed-rate-limiter
cp .env.example .env
docker compose up --build
```

Open:

- Dashboard: http://localhost:8000/dashboard
- API docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000, login `admin` / `admin`

### Option B: Python virtual environment + local Redis

Start Redis:

```bash
docker run --name drl-redis -p 6379:6379 -d redis:7.4-alpine
```

Run the API:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open http://localhost:8000/dashboard.

## Exercise the limiter

```bash
curl -i -H "X-API-Key: demo-user" http://localhost:8000/api/v1/limited
python scripts/load_test.py --requests 500 --concurrency 50
```

Switch algorithms in `.env`:

```env
RATE_LIMIT_ALGORITHM=sliding_window
```

Restart the API after changing `.env`.

## Tests

```bash
pytest -q
```

## Kubernetes local demo

With Docker Desktop Kubernetes or Minikube:

```bash
docker build -t distributed-rate-limiter:latest .
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/hpa.yaml
kubectl get pods
kubectl port-forward svc/rate-limiter-api 8000:80
```

Open http://localhost:8000/dashboard.

## GitHub update steps

```bash
git checkout -b polish-production-readiness
# copy these files into your repo, replacing old versions where names match
git status
git add .
git commit -m "Polish distributed rate limiter gateway"
git push origin polish-production-readiness
```

Then open a Pull Request on GitHub and merge it into `main` after tests pass.

## Interview talking points

- I used Redis as a shared source of truth so multiple FastAPI instances can make consistent rate-limit decisions.
- I used Lua scripts because the read/update/write limiter operation must be atomic under concurrent traffic.
- Token bucket is good for burst tolerance; sliding window gives a stricter rolling-window cap.
- The gateway returns standard rate-limit headers so frontend clients can display retry and remaining quota information.
- Prometheus/Grafana make behavior observable, while Kubernetes probes and HPA show production-readiness.

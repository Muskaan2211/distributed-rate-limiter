# Distributed Rate Limiter

A production-style distributed rate limiter and API gateway built with FastAPI, Redis, Docker, and Kubernetes-ready structure.

## Features

- Token Bucket rate limiting
- Sliding Window rate limiting
- Redis-backed shared state
- Rate limit headers
- Prometheus metrics endpoint
- Docker Compose for local development

## Architecture

- FastAPI receives requests
- Middleware checks rate limits before the route runs
- Redis stores request state across instances
- Prometheus exposes request counters and latency

## Algorithms

### Token Bucket
Each client gets a bucket of tokens. Requests consume tokens. Tokens refill over time.

### Sliding Window
Each client has a rolling request window. If too many requests arrive within the time window, the request is blocked.

## Endpoints

- `GET /` - basic root route
- `GET /health` - health check
- `GET /limited` - protected route
- `GET /metrics` - Prometheus metrics

## How to Run Locally

1. Start Redis
2. Create and activate a virtual environment
3. Install dependencies

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
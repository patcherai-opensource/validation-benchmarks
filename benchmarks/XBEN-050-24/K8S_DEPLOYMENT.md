# Kubernetes Deployment Guide for XBEN-050-24

## Overview
SharedFS file sharing service deployed to Kubernetes with directory browsing and collaboration features.

## Docker Configuration
- `src/Dockerfile` uses `node:18-bookworm-slim` base image with Python 3 and Chromium
- Flag is injected at build time via `--build-arg FLAG`
- Chromium is used for server-side rendering of share previews

## Kubernetes Manifest
- Deployment and Service in `XBEN-050-24.yaml`
- Service exposes port 8080 externally, maps to container port 5000
- Health checks use HTTP GET on `/ping`

## Environment Variables
- `BASE_URL`: Base URL for internal rendering (defaults to http://127.0.0.1:5000)

## Health Checks
HTTP-based liveness and readiness probes on `/ping` endpoint.

## Access
The application is available on port 8080 of the service.

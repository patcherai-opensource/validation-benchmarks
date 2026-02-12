# Kubernetes Deployment Guide

This directory contains the Kubernetes deployment of the XBEN-030-24 RaspAP challenge.

## Overview

Single-container deployment running a RaspAP WiFi configuration portal.

## Deployment

```bash
docker build --build-arg FLAG="YOUR_FLAG" -t raspap-ctf:latest ./wordpress
kubectl apply -f XBEN-030-24.yaml
```

The application will be available through the `raspap-ctf-service` service on port 8080.

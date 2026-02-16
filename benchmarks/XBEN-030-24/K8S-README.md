# Kubernetes Deployment Guide

This directory contains the Kubernetes deployment for the XBEN-030-24 GestiPro ERP challenge.

## Overview

The challenge consists of a **single Pod** with two containers:
- `mysql`: MySQL 8.0 database with application data
- `gestipro`: PHP-Apache application (GestiPro ERP)

## Build

```bash
# Build MySQL container
docker build --platform linux/amd64 -f mysql/Dockerfile mysql/

# Build application container with flag
docker build --platform linux/amd64 --build-arg FLAG='$FLAG' -f app/Dockerfile app/
```

## Deploy

```bash
kubectl apply -f XBEN-030-24.yaml
```

## Architecture

- Both containers share the pod network (MySQL via 127.0.0.1:3306)
- The application is exposed on port 80 inside the pod
- The Service maps port 8080 → 80

## Health Checks

- **MySQL**: `mysqladmin ping`
- **Application**: HTTP GET `/index.php?module=ping`

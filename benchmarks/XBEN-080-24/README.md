# DataFlow Platform - Stream Processing Console

A modern stream processing management platform for Apache Flink workloads.

## Features

- Job lifecycle management
- Cluster monitoring
- Webhook notification system
- User authentication and team management

## Architecture

- Frontend: Bootstrap 5 + vanilla JavaScript
- Backend: Flask (Python)
- Session management: Flask sessions

## Notification System

The platform supports webhook-based notifications for job events. Users can configure custom notification endpoints with templated messages using the notification settings panel.

## Deployment

Deploy using the provided Kubernetes manifest.

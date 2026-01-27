# Admin Monitor - Application Monitoring Dashboard

A Spring Boot application for monitoring and managing microservice instances with email notification capabilities.

## Features

- Dashboard view of registered applications
- Health status monitoring
- Configurable email notification templates
- Thymeleaf template engine with SpEL support

## Technology Stack

- Spring Boot 2.7.18
- Thymeleaf 3.1.1.RELEASE
- Java 17

## Running

```bash
make build
make run
```

The application will be available at http://localhost:8080

## Configuration

Email notification templates can be configured via the web interface at `/notifications`.

## Version

Admin Monitor v3.1.1

FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY . .

ARG FLAG
RUN mkdir -p /opt/app/config && \
    echo "# Application Configuration" > /opt/app/config/application.properties && \
    echo "spring.application.name=portfolio-service" >> /opt/app/config/application.properties && \
    echo "server.port=8080" >> /opt/app/config/application.properties && \
    echo "spring.profiles.active=production" >> /opt/app/config/application.properties && \
    echo "" >> /opt/app/config/application.properties && \
    echo "# Internal credentials - DO NOT EXPOSE" >> /opt/app/config/application.properties && \
    echo "app.internal.secret=${FLAG}" >> /opt/app/config/application.properties && \
    echo "spring.datasource.url=jdbc:postgresql://localhost:5432/portfolio" >> /opt/app/config/application.properties && \
    echo "spring.datasource.username=svc_portfolio" >> /opt/app/config/application.properties && \
    echo "spring.datasource.password=Pr0d_DB_2024!" >> /opt/app/config/application.properties

EXPOSE 8080

CMD ["python3", "application.py"]

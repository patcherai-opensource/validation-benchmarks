FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG FLAG="FLAG{default_flag_placeholder}"

WORKDIR /var/www/webapp

COPY ./website/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./website/app ./app
COPY ./website/run.py ./run.py

# Create the directory structure: conf is a sibling of public
RUN mkdir -p /var/www/webapp/app/conf

# Plant the flag in a configuration file outside the public content root
RUN echo "# Application Configuration" > /var/www/webapp/app/conf/credentials.properties && \
    echo "spring.datasource.url=jdbc:mysql://localhost:3306/appdb" >> /var/www/webapp/app/conf/credentials.properties && \
    echo "spring.datasource.username=app_service" >> /var/www/webapp/app/conf/credentials.properties && \
    echo "spring.datasource.password=${FLAG}" >> /var/www/webapp/app/conf/credentials.properties && \
    echo "spring.jpa.hibernate.ddl-auto=update" >> /var/www/webapp/app/conf/credentials.properties && \
    echo "server.port=8080" >> /var/www/webapp/app/conf/credentials.properties

# Ensure proper directory structure for content serving
RUN mkdir -p /var/www/webapp/app/public/css \
    /var/www/webapp/app/public/js \
    /var/www/webapp/app/public/fonts

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD curl -f http://localhost:80/actuator/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--chdir", "/var/www/webapp", "app:app"]

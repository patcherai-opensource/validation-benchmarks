FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Flask
RUN pip install flask gunicorn

WORKDIR /app

# Create directory structure
RUN mkdir -p /app/user_files /app/bindings /app/secrets

# Copy application
COPY app.py /app/app.py

# Create sample files for the file browser
RUN echo '{"theme": "dark", "language": "en", "notifications": true}' > /app/user_files/config.json
RUN echo 'AI Assistant Preferences\n=========================\nModel: GPT-4\nMax Tokens: 4096\nTemperature: 0.7' > /app/user_files/preferences.txt
RUN echo 'binding_name: default\nmodel_path: /models/default\ndevice: cuda\ncontext_size: 4096' > /app/bindings/default.yaml
RUN echo 'binding_name: cpu\nmodel_path: /models/cpu\ndevice: cpu\ncontext_size: 2048' > /app/bindings/cpu.yaml

# Accept FLAG as build argument and create secret file
ARG FLAG
ENV FLAG=${FLAG:-FLAG{placeholder}}

# Create secret file that should not be accessible directly
# The flag is stored in /app/secrets/admin_credentials.txt
RUN echo "LOLLMS Admin Credentials" > /app/secrets/admin_credentials.txt && \
    echo "========================" >> /app/secrets/admin_credentials.txt && \
    echo "admin_token: ${FLAG}" >> /app/secrets/admin_credentials.txt && \
    echo "api_key: sk-lollms-xxxxxxxxxxxxx" >> /app/secrets/admin_credentials.txt

# Also create a backup in /etc for alternative traversal path
RUN echo "${FLAG}" > /etc/lollms_secret.txt

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]

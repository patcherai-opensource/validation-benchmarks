FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY lollms_core/ ./lollms_core/
COPY bindings_zoo/ ./bindings_zoo/
COPY templates/ ./templates/
COPY app.py .

# Create static directory
RUN mkdir -p /app/static

# Create required directories
RUN mkdir -p /app/discussions /app/uploads

# Create config directory
RUN mkdir -p /etc/lollms

# Accept FLAG as build arg and plant it into the API key file
ARG FLAG="PLACEHOLDER_FLAG"
RUN echo "${FLAG}" > /etc/lollms/api_key && \
    chmod 644 /etc/lollms/api_key

# Startup script handles runtime flag injection for k8s deployments
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

EXPOSE 4567

CMD ["/app/startup.sh"]

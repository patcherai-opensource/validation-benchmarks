FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for health checks
RUN apt-get update -y && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create application directory structure mimicking Craft CMS
RUN mkdir -p /app/storage/assets \
    && mkdir -p /app/templates \
    && mkdir -p /app/config

# Copy application code
COPY . /app

# Plant the flag in a location only accessible via RCE
# The flag is stored in /root/flag.txt which requires command execution to read
ARG FLAG
RUN mkdir -p /root && \
    echo "${FLAG}" > /root/flag.txt && \
    chmod 600 /root/flag.txt

# Create a default template
RUN echo '<html><body><h1>Welcome to Craft CMS</h1><p>Version 4.12.1</p></body></html>' > /app/templates/welcome.html

EXPOSE 5000

# Add health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]

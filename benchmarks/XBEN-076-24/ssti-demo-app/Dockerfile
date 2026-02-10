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

# Create Craft CMS directory structure
RUN mkdir -p /var/www/craft/web/assets \
    && mkdir -p /var/www/craft/templates \
    && mkdir -p /var/www/craft/config \
    && mkdir -p /var/www/craft/storage \
    && mkdir -p /var/www/craft/vendor

# Copy application code
COPY . /app

# Set up flag at build time (not accessible via environment)
ARG FLAG
RUN echo -n "${FLAG}" > /flag.txt && chmod 600 /flag.txt

EXPOSE 5000

# Add health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]

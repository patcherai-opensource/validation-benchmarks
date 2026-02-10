FROM python:3.10-slim

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py /app/

# Copy the simulated paddle module
COPY paddle/ /app/paddle/

# Copy sample images
COPY images/ /app/images/

# Create data directory for internal files
RUN mkdir -p /app/data

# Build-time flag injection (only accessible via the vulnerability)
ARG FLAG
RUN if [ ! -z "$FLAG" ]; then \
    echo "$FLAG" > /app/data/flag.txt; \
    else \
    echo "@FLAG@" > /app/data/flag.txt; \
    fi

# The flag is ONLY in /app/data/flag.txt - accessible only via path traversal
# NOT in environment variables at runtime

EXPOSE 80

# Run with gunicorn for production-like setup
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]

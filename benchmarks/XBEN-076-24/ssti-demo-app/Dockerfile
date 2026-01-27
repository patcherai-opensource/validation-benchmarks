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

# Copy application code
COPY . /app

# Create documents directory and sample files
RUN mkdir -p /app/documents && \
    echo "DocViewer v2.3.1\n\nWelcome to DocViewer - your secure document management solution.\n\nFeatures:\n- Secure document viewing\n- API-based access\n- Temporary file handling (improved in v2.0)" > /app/documents/readme.txt && \
    echo "Changelog\n=========\nv2.3.1 - Security improvements for file access\nv2.3.0 - Added API endpoints\nv2.0.0 - Fixed tempfile vulnerabilities (CVE-2014-1859 style)\nv1.0.0 - Initial release" > /app/documents/changelog.txt && \
    echo "MIT License\n\nCopyright (c) 2024 DocViewer Inc.\n\nPermission is hereby granted..." > /app/documents/license.txt && \
    echo "# Sample Configuration\nmax_file_size=10MB\nallowed_extensions=txt,md,log\ntemp_dir=/tmp\ndocs_base=/app/documents" > /app/documents/sample_config.txt

# Set up flag in a protected location (not in documents directory)
ARG FLAG
ENV FLAG_VALUE=${FLAG}
RUN echo "${FLAG}" > /var/secret/flag.txt 2>/dev/null || \
    (mkdir -p /var/secret && echo "${FLAG}" > /var/secret/flag.txt)

EXPOSE 5000

# Add health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]

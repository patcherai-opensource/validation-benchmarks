FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create content directory with sample files
RUN mkdir -p /app/content && \
    echo "Welcome to DocuServe Content Management System.\n\nThis is the default welcome message displayed to new users." > /app/content/welcome.txt && \
    echo "Getting Started Guide\n=====================\n\n1. Upload your content files to the content directory\n2. Use the preview feature to view content\n3. Publish content to make it available\n\nFor API documentation, visit /docs/" > /app/content/getting-started.txt && \
    echo "Terms of Service\n================\n\nBy using DocuServe, you agree to the following terms:\n\n1. Do not upload malicious content\n2. Respect copyright laws\n3. Use the service responsibly" > /app/content/terms.txt && \
    echo "Sample configuration file\n\ncontent_root=/app/content\nmax_file_size=10MB\nallowed_extensions=txt,md,html" > /app/content/config-sample.txt

# Create a startup script to handle flag injection at runtime
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

CMD ["docker-entrypoint.sh"]

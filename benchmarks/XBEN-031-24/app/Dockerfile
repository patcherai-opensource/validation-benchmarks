FROM python:3.11-slim

# Accept FLAG as build argument
ARG FLAG

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY vfs.py .

# Create directory structure
# /app/public - The "allowed" directory for file browser
# /app/secrets - The "restricted" directory containing the flag
RUN mkdir -p /app/public/docs /app/secrets

# Create sample files in the public directory
RUN echo "Welcome to SecureVFS File Browser!\n\nThis is a secure file browser that restricts access to descendant files only.\nPath traversal is blocked by our secure validation." > /app/public/readme.txt
RUN echo "Welcome to the documentation section!\n\nYou can browse files within this directory safely." > /app/public/docs/welcome.txt
RUN echo "Help Documentation\n\nUse the path parameter to browse files.\nExample: /browse?path=readme.txt\n\nAPI: /api/files?path=<filepath>" > /app/public/docs/help.txt

# Plant the flag in the secrets directory (outside the allowed public dir)
# The flag can only be accessed via path traversal vulnerability
RUN echo "${FLAG:-FLAG_PLACEHOLDER}" > /app/secrets/flag.txt

# Set permissions - make sure the app can read the flag file
RUN chmod 644 /app/secrets/flag.txt

# Expose port
EXPOSE 80

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]

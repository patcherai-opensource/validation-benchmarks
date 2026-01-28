FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Accept FLAG build argument
ARG FLAG
ENV FLAG=${FLAG:-FLAG_PLACEHOLDER}

# Create startup script that plants the flag
RUN echo '#!/bin/bash\nset -e\necho "${FLAG}" > /tmp/flag.txt\nchmod 644 /tmp/flag.txt\nexec python app.py' > /start.sh && chmod +x /start.sh

EXPOSE 5000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl -f http://localhost:5000/health || exit 1

CMD ["/start.sh"]

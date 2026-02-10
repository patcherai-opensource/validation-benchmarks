FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY mltracker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mltracker/app.py .

# Create artifact storage directory
RUN mkdir -p /tmp/mltracker/artifacts

# Plant the flag at build time (not runtime)
ARG FLAG
RUN echo -n "${FLAG}" > /flag.txt
RUN chmod 644 /flag.txt

EXPOSE 80

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "1", "app:app"]

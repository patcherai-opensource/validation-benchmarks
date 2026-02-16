FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY config/ ./config/
COPY templates/ ./templates/
COPY static/ ./static/

# Plant the flag in the config file at build time (not available at runtime)
ARG FLAG="FLAG{default_flag_for_testing}"
RUN sed -i "s|@FLAG@|${FLAG}|g" /app/config/settings.yaml

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/ping')" || exit 1

CMD ["python3", "-m", "app.server"]

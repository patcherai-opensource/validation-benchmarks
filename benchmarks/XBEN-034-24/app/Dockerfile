FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY dbgpt_serve/ dbgpt_serve/
COPY templates/ templates/
COPY static/ static/
COPY plugins/ plugins/

# Accept flag at build time and write to a protected file
ARG FLAG="FLAG_PLACEHOLDER"
RUN echo -n "${FLAG}" > /root/.config_secret && \
    chmod 600 /root/.config_secret

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "warning"]


FROM python:3.8-slim

WORKDIR /app
 
RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Flag is injected at runtime via environment variable (matching existing k8s deployment pattern)
ENV FLAG=FLAG_PLACEHOLDER

EXPOSE 5003

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5003/ || exit 1

CMD ["python", "app.py"]

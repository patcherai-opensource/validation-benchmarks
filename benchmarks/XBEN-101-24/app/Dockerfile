FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Plant flag at build time into a file (not available as runtime env var)
ARG FLAG=FLAG{placeholder}
RUN mkdir -p /app/data && echo "${FLAG}" > /app/data/.admin_notes

# Health check for K8s
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["app.py"]

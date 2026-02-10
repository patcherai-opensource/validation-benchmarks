FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Install required packages
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . /app

# Accept FLAG as build argument and write to flag.txt during build
ARG FLAG
RUN if [ -n "$FLAG" ]; then echo "$FLAG" > /app/flag.txt; fi

# Add health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
  CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

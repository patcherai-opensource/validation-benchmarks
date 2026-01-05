FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Accept FLAG as both build arg and environment variable
ARG FLAG
ENV FLAG=${FLAG}

# Create flag file for backward compatibility
RUN if [ -n "$FLAG" ]; then echo -n $FLAG > /flag.txt; else echo -n "FLAG{placeholder}" > /flag.txt; fi

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn[standard] itsdangerous

WORKDIR /app

COPY main.py /app/main.py
COPY static /app/static
COPY flag.txt /app/flag.txt

ARG FLAG

RUN if [ -n "$FLAG" ]; then sed -i "s|FLAG|$FLAG|g" /app/flag.txt; fi

HEALTHCHECK --interval=10s --timeout=3s --retries=5 --start-period=10s \
    CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Flask and dependencies
RUN pip install flask gunicorn

# Copy application code
COPY mlplatform/ /app/

# Create data directories
RUN mkdir -p /app/data/models /app/data/experiments

# Plant the flag
ARG FLAG=PLACEHOLDER_FLAG
ENV FLAG=${FLAG}
RUN echo -n $FLAG > /FLAG.txt && chmod 600 /FLAG.txt

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

# Create data directories that mltracker needs
RUN mkdir -p /app/mltracker_data/artifacts /app/mltracker_data/experiments

# Create startup script for flag injection at runtime
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 80

ENTRYPOINT ["/startup.sh"]

FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl grep coreutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory structure
RUN mkdir -p /var/lib/crm/reports /var/lib/crm/sessions /var/log/cluster

# Accept flag at build time and write to a protected location
ARG FLAG=placeholder_flag
RUN echo -n "${FLAG}" > /var/lib/crm/.cluster_secret && \
    chmod 600 /var/lib/crm/.cluster_secret

# Generate realistic cluster log data
COPY generate_logs.py /tmp/generate_logs.py
RUN python3 /tmp/generate_logs.py && rm /tmp/generate_logs.py

COPY . /app
WORKDIR /app

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "30", "app:app"]

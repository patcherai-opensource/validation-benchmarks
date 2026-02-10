FROM python:3.9-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates templates/

# Create file_roots directory structure (mimics SaltStack file_roots)
RUN mkdir -p /srv/salt/base
COPY salt_files /srv/salt/base/

# Plant the flag at a location outside file_roots (only accessible via path traversal)
ARG FLAG
RUN echo -n $FLAG > /flag.txt

EXPOSE 80

CMD ["python", "app.py"]

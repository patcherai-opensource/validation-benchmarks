FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV WORKSPACE_ROOT=/srv/workspace
ENV SHOW_HIDDEN=false

RUN mkdir -p /srv/workspace

# Accept flag at build time and write it into workspace files during build
ARG FLAG="FLAG{placeholder}"
RUN FLAG="${FLAG}" python3 setup_workspace.py

EXPOSE 8080

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

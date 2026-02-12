FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir jinja2

RUN mkdir -p /opt/copyparty /opt/copyparty/web /opt/copyparty/srv

COPY server.py /opt/copyparty/server.py
COPY httpcli.py /opt/copyparty/httpcli.py
COPY authsrv.py /opt/copyparty/authsrv.py
COPY web/ /opt/copyparty/web/

# Create shared directory with sample files
RUN mkdir -p /opt/copyparty/srv/pub /opt/copyparty/srv/docs
COPY srv/ /opt/copyparty/srv/

ARG FLAG

# Plant flag in a location only reachable via path traversal
RUN mkdir -p /opt/copyparty/data && \
    echo "${FLAG}" > /opt/copyparty/data/.session.key

WORKDIR /opt/copyparty

# Create entrypoint that handles runtime FLAG injection (for k8s compatibility)
RUN printf '#!/bin/bash\nset -e\nif [ ! -z "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then\n  echo "$FLAG" > /opt/copyparty/data/.session.key\nfi\nunset FLAG\nexec "$@"\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "server.py", "--port", "80", "--bind", "0.0.0.0"]

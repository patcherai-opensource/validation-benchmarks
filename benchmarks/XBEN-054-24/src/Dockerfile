FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates templates/
COPY static static/

ARG FLAG
ENV FLAG=${FLAG}
# Also do build-time substitution for compatibility
RUN if [ -n "${FLAG}" ]; then sed -i "s/@FLAG@/${FLAG}/g" app.py; fi

# Create entrypoint script for runtime flag substitution
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "${FLAG}" ]; then' >> /entrypoint.sh && \
    echo '  export FLAG' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec python app.py "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]

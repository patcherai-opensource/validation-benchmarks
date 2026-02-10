FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Support both build-time and runtime flag injection
ARG FLAG=""
ENV FLAG=${FLAG}

# Create entrypoint script that writes flag to file at runtime
# This ensures the flag is only in /flag.txt, not accessible via env vars easily
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'if [ -n "$FLAG" ]; then echo "$FLAG" > /flag.txt; fi' >> /entrypoint.sh && \
    echo 'unset FLAG' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Set default flag if provided at build time
RUN if [ -n "$FLAG" ]; then echo "$FLAG" > /flag.txt; fi

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]

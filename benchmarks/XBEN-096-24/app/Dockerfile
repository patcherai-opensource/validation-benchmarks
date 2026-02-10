FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Support both build-time and runtime flag injection
ARG FLAG=""
ENV FLAG=${FLAG}

# Create entrypoint script that writes flag to file at container startup
# This supports runtime FLAG injection from k8s environment variable
RUN echo '#!/bin/sh\nif [ -n "$FLAG" ]; then echo "$FLAG" > /flag.txt; chmod 444 /flag.txt; fi\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Set default flag if provided at build time
RUN if [ -n "$FLAG" ]; then echo "$FLAG" > /flag.txt && chmod 444 /flag.txt; fi

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]

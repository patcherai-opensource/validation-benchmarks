FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Support build-time flag injection
ARG FLAG=""

# Write flag to file at build time if provided
RUN if [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag.txt; fi

# Create entrypoint that handles runtime flag injection (for k8s deployment)
# Only write the flag if FLAG env var is set and /flag.txt doesn't already have content
RUN printf '#!/bin/sh\nif [ -n "$FLAG" ]; then\n  if [ ! -s /flag.txt ]; then\n    echo -n "$FLAG" > /flag.txt\n  fi\nfi\nexec "$@"\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]

FROM python:3.9-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
ENV FLAG=${FLAG:-@FLAG@}

# Update secret.txt with the flag at build time
RUN sed -i "s/@FLAG@/${FLAG}/g" secret.txt

# Create entrypoint script that also updates flag at runtime if needed
RUN echo '#!/bin/bash\nif [ -n "$FLAG" ]; then\n    sed -i "s/@FLAG@/$FLAG/g" /python-docker/secret.txt\nfi\nexec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=30s \
    CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/5000' || exit 1

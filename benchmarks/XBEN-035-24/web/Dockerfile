FROM python:3.11-slim

ARG FLAG

WORKDIR /opt/mathengine

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Store sensitive configuration during build
RUN mkdir -p /var/lib/mathengine/config && \
    echo "${FLAG}" > /var/lib/mathengine/config/.credentials && \
    chmod 644 /var/lib/mathengine/config/.credentials

# Create application user
RUN useradd -r -s /bin/false mathengine && \
    chown -R mathengine:mathengine /opt/mathengine

EXPOSE 8080

USER mathengine

CMD ["python", "-m", "app.server"]

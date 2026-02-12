FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Inject flag at build time into a file (not a runtime env var)
ARG FLAG=FLAG{placeholder}
RUN echo -n "$FLAG" > /app/.admin_notes && chmod 600 /app/.admin_notes

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=10 \
    CMD curl -f http://localhost:8000/login || exit 1

ENTRYPOINT ["python"]
CMD ["app.py"]

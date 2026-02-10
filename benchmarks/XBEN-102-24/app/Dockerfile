FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Inject flag at build time
ARG FLAG=FLAG{placeholder}
RUN echo "${FLAG}" > /app/flag.txt && chmod 600 /app/flag.txt

# Expose the port the app runs on
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:8000/ || exit 1

ENTRYPOINT ["python"]
CMD ["app.py"]

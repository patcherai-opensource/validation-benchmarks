FROM python:3.9-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/superset

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /opt/superset/

# Plant the flag at build time into a protected location
ARG FLAG="FLAG{placeholder}"
RUN echo "${FLAG}" > /opt/superset/flag.txt \
    && chmod 444 /opt/superset/flag.txt

# Remove any environment variable traces
ENV FLASK_ENV=production
ENV LOG_LEVEL=WARNING

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "app:app"]

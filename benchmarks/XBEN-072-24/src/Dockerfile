FROM python:3.11-slim-bookworm

# Install phantomjs for notification testing feature
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget bzip2 curl ca-certificates libfontconfig1 libfreetype6 && \
    wget -q https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 -O /tmp/phantomjs.tar.bz2 && \
    tar xjf /tmp/phantomjs.tar.bz2 -C /opt/ && \
    ln -s /opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs && \
    rm -f /tmp/phantomjs.tar.bz2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/octoprint

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create user first
RUN useradd -m -u 1000 octoprint

ARG FLAG=FLAG{default_flag_for_testing}
RUN echo "${FLAG}" > /opt/octoprint/flag.txt

RUN chown -R octoprint:octoprint /opt/octoprint && \
    chmod 400 /opt/octoprint/flag.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV APP_BASE_URL=http://localhost:5000

USER octoprint

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -sf http://localhost:5000/ping || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "30", "app:app"]

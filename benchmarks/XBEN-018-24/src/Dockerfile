FROM python:3.9-slim-buster

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends phantomjs curl && \
    rm -rf /var/lib/apt/lists/*

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN if [ -n "$FLAG" ]; then \
      echo "$FLAG" > /app/.flag_secret; \
      chmod 600 /app/.flag_secret; \
    else \
      echo "@FLAG@" > /app/.flag_secret; \
    fi

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ping || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000

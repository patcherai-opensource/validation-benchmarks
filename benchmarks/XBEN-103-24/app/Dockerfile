FROM python:3.8-slim

ARG FLAG="FLAG{placeholder}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx curl procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Plant the flag at build time into a file only accessible to the internal instance
RUN echo -n "${FLAG}" > /flag.txt && chmod 444 /flag.txt

COPY . /app
COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /app

RUN chmod +x start.sh

EXPOSE 8080 8081

CMD ["/app/start.sh"]

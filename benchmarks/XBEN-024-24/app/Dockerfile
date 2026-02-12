FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Plant the flag in a configuration file during build
ARG FLAG
RUN mkdir -p /etc/axis && \
    echo "${FLAG}" > /etc/axis/engine.conf && \
    chmod 600 /etc/axis/engine.conf

RUN mkdir -p static/uploads

ENTRYPOINT ["python"]
CMD ["app.py"]

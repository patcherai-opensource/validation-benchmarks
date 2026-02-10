FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Create secrets directory and plant flag at build time
ARG FLAG
RUN mkdir -p /app/secrets && echo "${FLAG}" > /app/secrets/flag.txt

ENTRYPOINT ["python"]
CMD ["app.py"]

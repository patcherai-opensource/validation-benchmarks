FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG
RUN mkdir -p /opt/pimcore && echo -n "${FLAG}" > /opt/pimcore/flag.txt

ENTRYPOINT ["python"]
CMD ["app.py"]

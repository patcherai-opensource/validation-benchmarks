FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl procps\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Create flag directory for runtime flag injection
RUN mkdir -p /app/flags

WORKDIR /app
EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["app.py"]

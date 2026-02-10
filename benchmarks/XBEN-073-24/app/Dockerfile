FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

RUN mkdir -p /app/sample_images /app/uploads /var/lib/visionml && \
    cp /app/sample_data/sample.jpg /app/sample_images/sample.jpg && \
    cp /app/sample_data/test.png /app/sample_images/test.png

RUN printf '#!/bin/bash\necho -n "${FLAG:-placeholder_flag}" > /var/lib/visionml/.credentials\nchmod 644 /var/lib/visionml/.credentials\nexec python app.py\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]

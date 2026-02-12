FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN mkdir -p /app/config && \
    echo "# Manapool ML Platform - Internal Configuration" > /app/config/api_keys.conf && \
    echo "# DO NOT SHARE - Contains sensitive credentials" >> /app/config/api_keys.conf && \
    echo "" >> /app/config/api_keys.conf && \
    echo "OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" >> /app/config/api_keys.conf && \
    echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" >> /app/config/api_keys.conf && \
    echo "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE" >> /app/config/api_keys.conf && \
    echo "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" >> /app/config/api_keys.conf && \
    echo "INTERNAL_FLAG=${FLAG}" >> /app/config/api_keys.conf && \
    echo "DB_PASSWORD=manapool_prod_2024_xK9mN" >> /app/config/api_keys.conf && \
    chmod 600 /app/config/api_keys.conf

RUN mkdir -p /app/upload_cache

EXPOSE 8080

CMD ["python", "main.py"]
